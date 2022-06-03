#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 31 23:55:08 2022

@author: clarelin
"""

import pandas as pd
import music21 as m21
from itertools import combinations

from basic_information import simple_interval

INNER_VOICES = ['A', 'T']

def parallel_detection(df, voice_1, voice_2):
    parallel_detector = []
    interval_should_avoid = ['P1', 'P5']  # simpleName, P8==P1
    
    for i in df.index[:-1]:
        vertical_interval_1 =  m21.interval.Interval(noteStart=m21.note.Note(nameWithOctave=df[voice_1][i]),
                                 noteEnd=m21.note.Note(nameWithOctave=df[voice_2][i]))   
        vertical_interval_2 =  m21.interval.Interval(noteStart=m21.note.Note(nameWithOctave=df[voice_1][i+1]),
                                 noteEnd=m21.note.Note(nameWithOctave=df[voice_2][i+1])) 
        horizontal_interval_voice_1 = m21.interval.Interval(noteStart=m21.note.Note(nameWithOctave=df[voice_1][i]),
                                    noteEnd=m21.note.Note(nameWithOctave=df[voice_1][i+1]))
        horizontal_interval_voice_2 = m21.interval.Interval(noteStart=m21.note.Note(nameWithOctave=df[voice_2][i]),
                                    noteEnd=m21.note.Note(nameWithOctave=df[voice_2][i+1]))
        
        # do two voices go same direction?
        if horizontal_interval_voice_1.direction.name==horizontal_interval_voice_2.direction.name:
            wrong_type = 'Parallel'
        else:
            wrong_type = 'Contrary'  # 5ths and octaves by contrary motion should be avoided
            
        # are they consecutive intervals?
        if vertical_interval_1.directedName!=vertical_interval_2.directedName:
            continue
        # are the consecutive intervals P1, P5 (P8,...)?
        if vertical_interval_1.simpleName in interval_should_avoid:
            parallel_detector.append(pd.Series({
                'Voice 1': voice_1,
                'Voice 2': voice_2,
                'Place type': 'Horizontal',
                'Place': (i,i+1),
                'Wrong type': wrong_type,
                'Level': 'Wrong',
                'Remark': f"Interval {vertical_interval_1.niceName}",
                'Remark 2': f"Interval (in simpleName) {simple_interval(vertical_interval_1)}"
            }))
    if parallel_detector:
        return pd.concat(parallel_detector, axis=1).T
    
def hidden_detection(df, upper_voice, lower_voice):
    global INNER_VOICES
    
    # only check OUTTER_VOICES
    if upper_voice in INNER_VOICES:
        return
    if lower_voice in INNER_VOICES:
        return
    
    # make sure upper_voice=='S', lower_voice=='B':
    if upper_voice=='B' and lower_voice=='S':
        upper_voice, lower_voice = lower_voice, upper_voice
    
    hidden_detector = []
    interval_should_avoid = ['P1', 'P5']  # simpleName, P8==P1
    
    for i in df.index[:-1]:
        vertical_interval_1 =  m21.interval.Interval(noteStart=m21.note.Note(nameWithOctave=df[lower_voice][i]),
                                                     noteEnd=m21.note.Note(nameWithOctave=df[upper_voice][i])) 
        vertical_interval_2 =  m21.interval.Interval(noteStart=m21.note.Note(nameWithOctave=df[lower_voice][i+1]),
                                                     noteEnd=m21.note.Note(nameWithOctave=df[upper_voice][i+1])) 
        horizontal_interval_lower = m21.interval.Interval(noteStart=m21.note.Note(nameWithOctave=df[lower_voice][i]),
                                                         noteEnd=m21.note.Note(nameWithOctave=df[lower_voice][i+1]))
        horizontal_interval_upper = m21.interval.Interval(noteStart=m21.note.Note(nameWithOctave=df[upper_voice][i]),
                                                            noteEnd=m21.note.Note(nameWithOctave=df[upper_voice][i+1]))
        # do two voices go same direction?
        if horizontal_interval_lower.direction.name!=horizontal_interval_upper.direction.name:
            continue
        # are they consecutive intervals?
        if vertical_interval_1.directedName==vertical_interval_2.directedName:
            continue
        # does soprano go stepwise?
        if upper_voice=='S' and horizontal_interval_upper.isStep:
            continue
        # do the voices go into a interval should avoid?
        if vertical_interval_2.simpleName in interval_should_avoid:
            hidden_detector.append(pd.Series({
            'Voice 1': upper_voice,
            'Voice 2': lower_voice,
            'Place type': 'Horizontal',
            'Place': (i,i+1),
            'Wrong type': 'Hidden',
            'Level': 'Wrong',
            'Remark': f"Interval {vertical_interval_2.niceName}",
            'Remark 2': f"Interval (in simpleName) {simple_interval(vertical_interval_2)}"
        }))
    if hidden_detector:
        return pd.concat(hidden_detector, axis=1).T
    
def parallel_and_hidden_detection(VOICES, df):
    parallel_and_hidden = []

    # parallel intervals detection
    for voice_1, voice_2 in list(combinations(VOICES, 2)):
        temp = parallel_detection(df, voice_1, voice_2)
        if type(temp)!=type(None):
            parallel_and_hidden.append(temp)

    # hidden intervals detection: we only concern hidden intervals between soprano and bass
    temp = hidden_detection(df, 'S', 'B')
    if type(temp)!=type(None):
        parallel_and_hidden.append(temp)

    if parallel_and_hidden:
        return pd.concat(parallel_and_hidden).reset_index(drop=True)
    
