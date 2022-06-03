#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 31 23:53:58 2022

@author: clarelin
"""

import numpy as np
import pandas as pd
import music21 as m21

# (scale_degree, music21.figuredBass.notation.Notation.origNumbers)
L7 = [(1,(None,)), (5,(None,)), (5,(7,))]
L8 = [(1,(6,)), (5,(6,)), (5,(6,5)), (7,(6,))]
L9 = [(5,(4,3)), (5,(4,2))]  # including 43 & 42
L10 = [(2,(None,)), (2,(6,)), (4,(None,))]
#L11 = Cadential 64
L12 = [(4,(6,)), (6,(None,))]
L13 = [(2,(7,)), (4,(7,))]
L14 = [(2,(4,3)), (2,(4,2)), (2,(6,5)), (4,(4,3)), (4,(4,2)), (4,(6,5)), (6,(6,))]
RN_AVAILABLE = {  
    'L7': L7,
    'L8': L7 + L8,
    'L9': L7 + L8 + L9,
    'L10': L7 + L8 + L9 + L10,
    'L11': L7 + L8 + L9 + L10,
    'L12': L7 + L8 + L9 + L10 + L12,
    'L13': L7 + L8 + L9 + L10 + L12 + L13,
    'L14': L7 + L8 + L9 + L10 + L12 + L13 + L14
}

def find_inharmonic_notes(VOICES, chord_notes, expected_notes):  # 學生寫的和絃和他寫的和弦級數, 有沒有出現非和弦音
    '''only check if there is any inharmonic tone'''
    inharmonic_notes = []
    for idx,n in enumerate(chord_notes):
        if n not in expected_notes:
            inharmonic_notes.append((VOICES[idx], n))
    return inharmonic_notes

def chord_pitch_from_rn(rn):
    return [p.name for p in rn.pitches]

def chord_pitch_from_chord(chord):
    return [p.name for p in chord]

def roman_numerals_analysis(VOICES, df, key, lecture, leading_tone):
    global RN_AVAILABLE
    
    rna = []
    correct = []
    mixture_available = []
    missing_third_by_chord = []
    missing_third_by_rn = []
    missing_fifth_by_chord = []
    missing_fifth_by_rn = []
    inversion = []
    inharmonic_notes = []
    lecture_available_rn = []
    sevenths = []
    multiple_leading_tone = []
    multiple_seventh = []
    
    for idx in df.index:
        chord = m21.chord.Chord(df.loc[idx,VOICES].values)      # chord object: 學生寫的和弦, SATB得到的和弦級數: 如果缺音會判斷錯誤
        chord_notes = chord_pitch_from_chord(chord)             #         list: 該和弦的音名 (按順序, 由高至低, SATB)
        true_rn = m21.roman.romanNumeralFromChord(chord, key)   # roman object: 該和弦的和弦級數 (by RNA), r.figure=='V6'
        ans = df.loc[idx,'scale degree']                        #          str: 學生希望的和弦級數
        if pd.notnull(ans):
            expected_rn = m21.roman.RomanNumeral(ans, key)          # roman object: 學生希望的和弦級數
            expected_notes = chord_pitch_from_rn(expected_rn)       #         list:學生希望的和弦級數的音名 (按順序, 由低至高)
        
        rna.append(true_rn.figure)
        
        if pd.notnull(ans):        
            if ans==true_rn.figure:
                correct.append(True)
                mixture_available.append(True)
            else:
                correct.append(False)
                if m21.roman.RomanNumeral(ans, key).isMixture():
                    mixture_available.append(False)
                else:
                    mixture_available.append(True)
        else:
            correct.append(None)
            mixture_available.append(None)
            
        # 檢查是否符合該和聲單元
        if lecture in RN_AVAILABLE.keys():
            if true_rn.figuresNotationObj.origNumbers==(5,) and (not bool(chord.third)):  # 缺3音的三和弦
                lecture_available_rn.append((true_rn.scaleDegree, (None,)) in RN_AVAILABLE[lecture])
            else:
                lecture_available_rn.append((true_rn.scaleDegree, true_rn.figuresNotationObj.origNumbers) in RN_AVAILABLE[lecture])
        
        # 檢查是否缺3音?  - Wrong         
        missing_third_by_chord.append(not bool(chord.third))
        # 和 ans(學生寫的和弦級數) 比對
        if pd.notnull(ans):
            missing_third_by_rn.append(not(expected_rn.third.name in chord_notes))
        else:
            missing_third_by_rn.append(None)
        # 7和弦3音是可以的
        sevenths.append(chord.isSeventh())
        
        # 檢查是否缺5音?  - Warning
        missing_fifth_by_chord.append(not bool(chord.fifth))
        if pd.notnull(ans):
            missing_fifth_by_rn.append(not(expected_rn.fifth.name in chord_notes))
        else:
            missing_fifth_by_rn.append(None)
            
        # 檢查轉位
        if pd.notnull(ans):
            if true_rn.scaleDegree==expected_rn.scaleDegree:  # 若相同音級的和弦, 不論大/小、增/減、三/七
                inversion.append(chord[-1].name==expected_notes[0])
            else:
                inversion.append(False)
        else: inversion.append(None)
        
        # 檢查非和弦音
        if pd.notnull(ans):
            inharmonic_notes.append(find_inharmonic_notes(VOICES, chord_notes, expected_notes))
        else:
            inharmonic_notes.append(None)
        
        # 檢查導音是否重複
        items, counts = np.unique(chord_notes, return_counts=True)
        temp_dict = dict(zip(items, counts))
        if leading_tone in temp_dict.keys():
            if temp_dict[leading_tone] > 1:
                multiple_leading_tone.append(True)
            else:
                multiple_leading_tone.append(False)
        else:
            multiple_leading_tone.append(None) 
        # 檢查七和弦七音是否重複
        if true_rn.isSeventh():
            note_seventh = true_rn.seventh.name
            if note_seventh in temp_dict.keys():
                if temp_dict[note_seventh] > 1:
                    multiple_seventh.append(True)
                else:
                    multiple_seventh.append(False)
            else:
                multiple_seventh.append(None) 
        else:
            multiple_seventh.append(None)
        
        temp = {
            'rna': rna,
            '~correct': [not i for i in correct],
            '~mixture_available': [not i for i in mixture_available],
            '~lecture_available_rn': [not i for i in lecture_available_rn],
            'missing_third_by_chord': missing_third_by_chord,
            'missing_third_by_rn': missing_third_by_rn,
            'sevenths': sevenths,
            'missing_fifth_by_chord': missing_fifth_by_chord,
            'missing_fifth_by_rn': missing_fifth_by_rn,
            'wrong_inversion': [not i for i in inversion],
            'inharmonic_notes': inharmonic_notes,
            'multiple_leading_tone': multiple_leading_tone,
            'multiple_seventh': multiple_seventh
        }
    return  temp

def vertical_harmonic_related(VOICES, df_score, key, lecture, leading_tone):
    df = df_score.copy()
    temp = roman_numerals_analysis(VOICES, df, key, lecture, leading_tone)

    df['Roman numerals analysis'] = temp['rna']          # 從 SATB 判斷應該是什麼和弦級數
    df['Uncorrect'] = temp['~correct']                      # 學生寫的 scale degree 和 rna 是否一致
    df['Mixture unavailable'] = temp['~mixture_available']  # 學生寫的 scale degree 是否是該調性允許的級數
    if lecture:
        df['lecture_unavailable_rn'] = temp['~lecture_available_rn']
    df['missing_third_by_chord'] = temp['missing_third_by_chord']
    df['missing_third_by_rn'] = temp['missing_third_by_rn']
    df['sevenths'] = temp['sevenths']
    df['missing_fifth_by_chord'] = temp['missing_fifth_by_chord']
    df['missing_fifth_by_rn'] = temp['missing_fifth_by_rn']
    df['wrong_inversion'] = temp['wrong_inversion']
    df['inharmonic_notes'] = temp['inharmonic_notes']
    df['multiple_leading_tone'] = temp['multiple_leading_tone']
    df['multiple_seventh'] = temp['multiple_seventh']
    
    df['inharmonic_notes_bool'] = df.inharmonic_notes.apply(lambda x:bool(x))
    # 7和弦可以缺3音, 但仍然要放入warning
    third_warning = []
    for idx in df.index:
        if (df['missing_third_by_chord'][idx] or df['missing_third_by_rn'][idx]) and df['sevenths'][idx]:
            df.loc[idx,'missing_third_by_chord'] = False
            df.loc[idx,'missing_third_by_rn'] = False
            third_warning.append(True)
        else:
            third_warning.append(False)
            
    df['third_warning'] = third_warning
    wrong = ['Mixture unavailable', 'inharmonic_notes_bool', 'wrong_inversion',
         'missing_third_by_chord', 'missing_third_by_rn']
    warning = ['Uncorrect', 'missing_fifth_by_chord', 'missing_fifth_by_rn', 'third_warning']
    df['Wrong'] = [any([df[j][idx] for j in wrong]) for idx in df.index]
    df['Warning'] = [any([df[j][idx] for j in warning]) for idx in df.index]
    
    return df

def harmony_error_detection(df, lecture=False):
    harmony_error_detector = []
    for idx in df.index:
        if df['Wrong'][idx]:
            harmony_error_detector.append(pd.Series({
                'Voice 1': None,
                'Voice 2': None,
                'Place type': 'Vertical',
                'Place': idx,
                'Wrong type': 'Harmony',
                'Level': 'Wrong'
            }))
        if df['Warning'][idx]:
            harmony_error_detector.append(pd.Series({
                'Voice 1': None,
                'Voice 2': None,
                'Place type': 'Vertical',
                'Place': idx,
                'Wrong type': 'Harmony',
                'Level': 'Warning'
            }))
        if lecture:
            if df['lecture_unavailable_rn'][idx]:
                harmony_error_detector.append(pd.Series({
                    'Voice 1': None,
                    'Voice 2': None,
                    'Level': 'Warning',
                    'Place type': 'Vertical',
                    'Place': idx,
                    'Wrong type': 'lecture_unavailable_rn'
                }))   
        if df['multiple_leading_tone'][idx]:
            harmony_error_detector.append(pd.Series({
                'Voice 1': None,
                'Voice 2': None,
                'Level': 'Wrong',
                'Place type': 'Vertical',
                'Place': idx,
                'Wrong type': 'multiple_leading_tone'
            })) 
        if df['multiple_seventh'][idx]:
            harmony_error_detector.append(pd.Series({
                'Voice 1': None,
                'Voice 2': None,
                'Level': 'Wrong',
                'Place type': 'Vertical',
                'Place': idx,
                'Wrong type': 'multiple_seventh'
            }))  
            
    if harmony_error_detector:
        return pd.concat(harmony_error_detector, axis=1).T
    
    