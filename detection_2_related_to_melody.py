#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 31 23:51:03 2022

@author: clarelin
"""

import pandas as pd
import music21 as m21

from basic_information import simple_interval

OUTTER_VOICES = ['S', 'B']
INNER_VOICES = ['A', 'T']

def melody_interval_detection(VOICES, df, key, leading_tone):
    melody_interval_detector = []
    
    for v in VOICES:
        for idx in df.index[:-1]:
            level = 'Wrong'
            note_1 = m21.note.Note(nameWithOctave=df[v][idx])
            note_2 = m21.note.Note(nameWithOctave=df[v][idx+1])
            horizontal_interval =  m21.interval.Interval(noteStart=note_1,
                                                         noteEnd=note_2)

            if horizontal_interval.diatonic.specifierAbbreviation == 'A':
                if (abs(horizontal_interval.generic.directed)!=4) \
                  or (abs(horizontal_interval.generic.directed)==4 \
                      and (note_1.name!=leading_tone and note_2.name!=leading_tone)):  #包含導音的A4, d5 可接受
                    if (key.mode=='minor') \
                        and (abs(horizontal_interval.generic.directed)==2) \
                        and (leading_tone==horizontal_interval.noteStart.name \
                             or leading_tone==horizontal_interval.noteEnd.name):  # 小調遇導音增二度
                        level = 'Warning'
                    
                    melody_interval_detector.append(pd.Series({
                        'Voice 1': v,
                        'Voice 2': None,
                        'Place type': 'Horizontal',
                        'Place': (idx,idx+1),
                        'Wrong type': 'Melody interval',
                        'Level': level,
                        'Remark': f"Interval {horizontal_interval.niceName}",
                        'Remark 2': f"Interval (in simpleName) {simple_interval(horizontal_interval)}"
                    }))

            elif horizontal_interval.diatonic.specifierAbbreviation == 'd':
                if abs(horizontal_interval.generic.directed)!=5 \
                  or (abs(horizontal_interval.generic.directed)==5 \
                    and (note_1.name!=leading_tone and note_2.name!=leading_tone)):
                    melody_interval_detector.append(pd.Series({
                        'Voice 1': v,
                        'Voice 2': None,
                        'Place type': 'Horizontal',
                        'Place': (idx,idx+1),
                        'Wrong type': 'Melody interval',
                        'Level': level,
                        'Remark': f"Interval {horizontal_interval.niceName}",
                        'Remark 2': f"Interval (in simpleName) {simple_interval(horizontal_interval)}"
                    }))
            
    if melody_interval_detector:
        return pd.concat(melody_interval_detector, axis=1).T
    
def leading_tone_resolution_detection(VOICES, df, key, leading_tone):
    global OUTTER_VOICES
    leading_tone_resolution = []
    
    for v in VOICES:
        if v in OUTTER_VOICES:
            for idx in df.index[:-1]:
                level = 'Wrong'
                note_1 = m21.note.Note(nameWithOctave=df[v][idx])
                note_2 = m21.note.Note(nameWithOctave=df[v][idx+1])
                interval = m21.interval.Interval(noteStart=note_1, noteEnd=note_2)
                if (note_1.name==leading_tone.name) and ((note_2.name!=key.tonic.name) or interval.isSkip):
                    leading_tone_resolution.append(pd.Series({
                        'Voice 1': v,
                        'Voice 2': None,
                        'Place type': 'Horizontal',
                        'Place': (idx,idx+1),
                        'Wrong type': 'leading_tone_resolution',
                        'Level': level
                    }))

    if leading_tone_resolution:
        return pd.concat(leading_tone_resolution, axis=1).T
    
def leading_tone_minor_detection(VOICES, df, key, leading_tone):
    leading_tone_minor = []
    if key.mode=='minor':  # 檢查小調導音有沒有升高
        for v in VOICES:
            for idx in df.index:
                note_1 = m21.note.Note(nameWithOctave=df[v][idx])
                if key.getScale(mode=key.mode).getScaleDegreeFromPitch(note_1)==7 and note_1.name!=leading_tone:
                    leading_tone_minor.append(pd.Series({
                        'Voice 1': v,
                        'Voice 2': None,
                        'Place type': 'Vertical',
                        'Place': idx,
                        'Wrong type': 'leading_tone_error',
                        'Level': 'Wrong'
                    }))
    if leading_tone_minor:
        return pd.concat(leading_tone_minor, axis=1).T
    
def melody_jump_detection(VOICES, df):
    global OUTTER_VOICES
    global INNER_VOICES
    
    jump_detector = []
    for v in VOICES:
        for idx in df.index[1:-1]:
            horizontal_interval_1 =  m21.interval.Interval(noteStart=m21.note.Note(nameWithOctave=df[v][idx-1]),
                                      noteEnd=m21.note.Note(nameWithOctave=df[v][idx])) 
            horizontal_interval_2 =  m21.interval.Interval(noteStart=m21.note.Note(nameWithOctave=df[v][idx]),
                                    noteEnd=m21.note.Note(nameWithOctave=df[v][idx+1]))

            if v in OUTTER_VOICES:
                if abs(horizontal_interval_1.generic.directed) < 6:  # 不是大跳
                      continue
                elif abs(horizontal_interval_1.generic.directed)<=8 \
                 and abs(horizontal_interval_1.generic.directed) >= 6:  # 合理大跳
                    if horizontal_interval_1.direction.name != horizontal_interval_2.direction.name:  # 有反向
                        if abs(horizontal_interval_2.generic.directed) >= 6:  # 反向後沒有小跳
                            jump_detector.append(pd.Series({
                                'Voice 1': v,
                                'Voice 2': None,
                                'Place type': 'Horizontal',
                                'Place': (idx,idx+1),
                                'Wrong type': 'Melody_violate_error_jump',
                                'Level': 'Wrong',
                                'Remark': f"Interval {horizontal_interval_2.niceName}",
                                'Remark 2': f"Interval (in simpleName) {simple_interval(horizontal_interval_2)}"
                            }))
                    else:  # 沒有反向
                        jump_detector.append(pd.Series({
                            'Voice 1': v,
                            'Voice 2': None,
                            'Place type': 'Horizontal',
                            'Place': (idx,idx+1),
                            'Wrong type': 'Melody_violate_error_direction',
                            'Level': 'Wrong',
                            'Remark': f"Interval {horizontal_interval_2.niceName}",
                            'Remark 2': f"Interval (in simpleName) {simple_interval(horizontal_interval_2)}"
                        }))
                else:  # 跳超過八度
                    jump_detector.append(pd.Series({
                        'Voice 1': v,
                        'Voice 2': None,
                        'Place type': 'Horizontal',
                        'Place': (idx-1,idx),
                        'Wrong type': 'Melody_violate_big_jump',
                        'Level': 'Wrong',
                        'Remark': f"Interval {horizontal_interval_1.niceName}",
                        'Remark 2': f"Interval (in simpleName) {simple_interval(horizontal_interval_1)}"
                    }))
                    
            elif v in INNER_VOICES:
                if abs(horizontal_interval_1.generic.directed) > 5:  # 內聲部不可跳超過5度
                    jump_detector.append(pd.Series({
                        'Voice 1': v,
                        'Voice 2': None,
                        'Place type': 'Horizontal',
                        'Place': (idx-1,idx),
                        'Wrong type': 'Melody_violate_big_jump',
                        'Level': 'Wrong',
                        'Remark': f"Interval {horizontal_interval_1.niceName}",
                        'Remark 2': f"Interval (in simpleName) {simple_interval(horizontal_interval_1)}"
                    }))
                    
    if jump_detector:
        return pd.concat(jump_detector, axis=1).T
    
