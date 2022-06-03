#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 31 23:47:53 2022

@author: clarelin
"""

import pandas as pd
import music21 as m21

def vocal_range_detection(VOICES, df):
    ALLOWABLE_EXTENSIONS = {
        'S': {'lower_note': 'B3', 'higher_note': 'A5'},
        'A': {'lower_note': 'G3', 'higher_note': 'D5'},
        'T': {'lower_note': 'C3', 'higher_note': 'A4'},
        'B': {'lower_note': 'D2', 'higher_note': 'D4'}
    }
    
    vocal_range_detector = []
    for v in VOICES:
        lower_note = m21.note.Note(ALLOWABLE_EXTENSIONS[v]['lower_note'])
        higher_note = m21.note.Note(ALLOWABLE_EXTENSIONS[v]['higher_note'])
        for idx,n in enumerate(df[v]):
            current_note = m21.note.Note(n)
            compared_with_lower_note = m21.interval.Interval(noteStart=lower_note, noteEnd=current_note)
            if compared_with_lower_note.direction.value < 0:  # 超過下限
                vocal_range_detector.append(pd.Series({
                    'Voice 1': v,
                    'Voice 2': None,
                    'Place type': 'Vertical',
                    'Place': idx,
                    'Wrong type': 'Vocal range',
                    'Level': 'Wrong',
                    'Remark': f"note {current_note.nameWithOctave} lower than lower bound {lower_note.nameWithOctave}"
                }))

            compared_with_higher_note = m21.interval.Interval(noteStart=current_note, noteEnd=higher_note)
            if compared_with_higher_note.direction.value < 0:  # 超過上限
                vocal_range_detector.append(pd.Series({
                    'Voice 1': v,
                    'Voice 2': None,
                    'Place type': 'Vertical',
                    'Place': idx,
                    'Wrong type': 'Vocal range',
                    'Level': 'Wrong',
                    'Remark': f"note {current_note.nameWithOctave} higher than upper bound {higher_note.nameWithOctave}"
                }))

    if vocal_range_detector:
        return pd.concat(vocal_range_detector, axis=1).T
    
def spacing_detection(VOICES, df):
    SPACEING = {
        ('S', 'A'): 'P8',
        ('A', 'T'): 'P8',
        ('T', 'B'): 'P12'
    }
    spacing_detector = []
    for v, voice_1 in enumerate(VOICES[:-1]):
        voice_2 = VOICES[v+1]
        allowable_spacing = m21.interval.Interval(SPACEING[(voice_1, voice_2)])
        
        for idx in df.index:
            higher_note = m21.note.Note(df[voice_1][idx])
            lower_note = m21.note.Note(df[voice_2][idx])
            vertical_interval = m21.interval.Interval(noteStart=lower_note, noteEnd=higher_note)
            if m21.interval.subtract([allowable_spacing,vertical_interval]).direction.value < 0:
                spacing_detector.append(pd.Series({
                        'Voice 1': voice_1,
                        'Voice 2': voice_2,
                        'Place type': 'Vertical',
                        'Place': idx,
                        'Wrong type': 'Spacing',
                        'Level': 'Wrong',
                        'Remark': f"{vertical_interval.name} is bigger than allowable spacing {allowable_spacing.name}"
                    }))
    if spacing_detector:
        return pd.concat(spacing_detector, axis=1).T
    
    
def voice_crossing_detection(VOICES, df):
    voice_crossing_detector = []
    for v, voice_1 in enumerate(VOICES[:-1]):
        voice_2 = VOICES[v+1]
        for idx in df.index:
            higher_note = m21.note.Note(df[voice_1][idx])
            lower_note = m21.note.Note(df[voice_2][idx])
            vertical_interval = m21.interval.Interval(noteStart=lower_note, noteEnd=higher_note)

            if vertical_interval.direction.value < 0:
                voice_crossing_detector.append(pd.Series({
                        'Voice 1': voice_1,
                        'Voice 2': voice_2,
                        'Place type': 'Vertical',
                        'Place': idx,
                        'Wrong type': 'Voice crossing',
                        'Level': 'Wrong',
                        'Remark': f"{voice_1}: {higher_note.nameWithOctave} is lower than {voice_2}: {lower_note.nameWithOctave}"
                    }))
    if voice_crossing_detector:
        return pd.concat(voice_crossing_detector, axis=1).T
    
def overlapping_detection_inner_function(df, voice_1, voice_2): 
    '''voice_1 is upper voice, voice_2 is lower voice'''
    
    overlapping_detector = []

    for i in df.index[:-1]:
            horizontal_interval_voice_1 = m21.interval.Interval(noteStart=m21.note.Note(nameWithOctave=df[voice_1][i]),
                                        noteEnd=m21.note.Note(nameWithOctave=df[voice_1][i+1]))
            horizontal_interval_voice_2 = m21.interval.Interval(noteStart=m21.note.Note(nameWithOctave=df[voice_2][i]),
                                        noteEnd=m21.note.Note(nameWithOctave=df[voice_2][i+1]))

            # do two voices go same direction?
            if horizontal_interval_voice_1.direction.name==horizontal_interval_voice_2.direction.name:
                if (horizontal_interval_voice_1.direction.value>0) or (horizontal_interval_voice_2.direction>0):    # 上行
                    expected_higher_note = m21.note.Note(df[voice_1][i])
                    expected_lower_note = m21.note.Note(df[voice_2][i+1])
                    interval = m21.interval.Interval(noteStart=expected_lower_note, noteEnd=expected_higher_note)
                    if interval.direction.value < 0:
                        overlapping_detector.append(pd.Series({
                            'Voice 1': voice_1,
                            'Voice 2': voice_2,
                            'Place type': 'Horizontal',
                            'Place': (i, i+1),
                            'Wrong type': 'Overlapping',
                            'Level': 'Wrong',
                            'Remark': f"{voice_2}: {expected_lower_note.nameWithOctave} at {i+1} is higher than {voice_1}: {expected_higher_note.nameWithOctave} at {i}"
                        }))

                elif (horizontal_interval_voice_1.direction.value>0) or (horizontal_interval_voice_2.direction>0):  # 下行
                    expected_higher_note = m21.note.Note(df[voice_1][i+1])
                    expected_lower_note = m21.note.Note(df[voice_2][i])
                    interval = m21.interval.Interval(noteStart=expected_lower_note, noteEnd=expected_higher_note)
                    if interval.direction.value < 0:
                        overlapping_detector.append(pd.Series({
                            'Voice 1': voice_1,
                            'Voice 2': voice_2,
                            'Place type': 'Horizontal',
                            'Place': (i, i+1),
                            'Wrong type': 'Overlapping',
                            'Level': 'Wrong',
                            'Remark': f"{voice_1}: {expected_higher_note.nameWithOctave} at {i+1} is lower than {voice_2}: {expected_lower_note.nameWithOctave} at {i}"
                        }))
                else:  # 有一聲部沒有移動. 如果越位, 必定交越, 所以不用檢查.
                    continue

    if overlapping_detector:
        return pd.concat(overlapping_detector, axis=1).T
    

def overlapping_detection(VOICES, df):
    overlapping_detector = []
    for v, voice_1 in enumerate(VOICES[:-1]):
        voice_2 = VOICES[v+1]
        temp = overlapping_detection_inner_function(df, voice_1, voice_2)
        if type(temp)!=type(None):
            overlapping_detector.append(temp)

    if overlapping_detector:
        return pd.concat(overlapping_detector).reset_index(drop=True)


