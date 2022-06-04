#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 31 23:46:10 2022

@author: clarelin
"""

import sys
import numpy as np
import pandas as pd
import music21 as m21

#FOUR_PART_VOICES = ['S', 'A', 'T', 'B']
#OUTTER_VOICES = ['S', 'B']
#INNER_VOICES = ['A', 'T']

WRONG_TYPE = {
    'Vocal range': '個別音域',
    'Spacing': '音域配置',
    'Voice crossing': '交越',
    'Overlapping': '越位',
    'Melody interval': '單聲部橫向旋律包含增減音程',
    'Melody_violate_error_jump': '大跳後無反向小跳或級進',
    'Melody_violate_error_direction': '大跳後無反向',
    'Melody_violate_big_jump': '聲部大跳違反原則',
    'Parallel': '平行一五八',
    'Contrary': '反向八五度',
    'Hidden': '隱伏八五度(外聲部)',
    'Harmony': '和聲方面有問題',
    'lecture_unavailable_rn': '實際使用的和弦級數超出單元範圍',
    'multiple_leading_tone': '導音重複',
    'multiple_seventh': '七和弦七音重複',
    'leading_tone_error': '小調導音未升高',
    'leading_tone_resolution': '外聲部導音沒有解決至主音'
}


# In[]

def detect_key_by_key_sign(key_sign, question_type, VOICES, df, key_student):
    '''從調號推測'''
    possible_key_major = key_sign.asKey()
    possible_key_minor = key_sign.asKey(mode='minor')  # natural form
    possible_key_minor.abstract = m21.scale.AbstractHarmonicMinorScale()  # turn to harmonic scale
    #minor_leading_tone = possible_key_minor.pitchesFromScaleDegrees([7])[0].name  # 導音
    minor_leading_tone = possible_key_minor.getLeadingTone().name
    print(f"possible_key_major: {possible_key_major}")  #, major_leading_tone: {major_leading_tone}")  
    print(f"possible_key_minor: {possible_key_minor}, minor_leading_tone: {minor_leading_tone}")
    
    if pd.notna(question_type):  # 題目有提供高音題 or 低音題
        if question_type=='B':   # 低音題: 因為必結束在一級原位, 直接看最後一個音即可
            ending_note = m21.note.Note(df.iloc[-1,:][question_type]).name
            if ending_note==possible_key_major.tonic.name:
                key = possible_key_major
            elif ending_note==possible_key_minor.tonic.name:
                key = possible_key_minor
            else:
                sys.stderr.write(f"something wrong with question_type {question_type} and the ending note {ending_note}")
                # 從寫作內容判斷調性
                key = detect_key_by_ending_chord(df, VOICES, key_sign, minor_leading_tone, key_student,
                                                  possible_key_major, possible_key_minor)

        elif question_type=='S': # 高音題: 不一定在音級1
            ending_note = m21.note.Note(df.iloc[-1,:][question_type]).name
            if ending_note==possible_key_major.pitchFromDegree(5).name:  # 大調 音級5
                key = possible_key_major
            elif ending_note==possible_key_minor.tonic.name:                  # 小調 音級1
                key = possible_key_minor
            else:                                                         # 大調 音級 1,3 == 小調音級 3,5
                # 看 S 旋律中有沒有導音升高 -> 有: 小調, 沒有: 大調. 預設未知
                key = detect_key_by_melody(None, df, VOICES, minor_leading_tone, possible_key_minor)
                # 從寫作內容判斷調性: 看最後一個和弦
                if not key:
                    key = detect_key_by_ending_chord(df, VOICES, key_sign, minor_leading_tone, key_student,
                                                  possible_key_major, possible_key_minor)
        
        else:  # question_type 讀取異常 (只允許 np.nan, 'S', 'B')
            sys.stderr.write(f"something wrong with question_type {question_type}")
            # 從寫作內容判斷調性: 看最後一個和弦
            key = detect_key_by_ending_chord(df, VOICES, key_sign, minor_leading_tone, key_student,
                                                  possible_key_major, possible_key_minor)
            
    else:  # 題目沒有提供高音題 or 低音題, 從寫作內容判斷調性: 看最後一個和弦
        key = detect_key_by_ending_chord(df, VOICES, key_sign, minor_leading_tone,  key_student,
                                                  possible_key_major, possible_key_minor)
    
    return key

def detect_key_by_melody(key_detected, df, VOICES, minor_leading_tone, possible_key_minor):
    '''看旋律中有沒有導音升高 -> 有: 小調, 沒有: 大調'''
    for n in df[VOICES].to_numpy().flatten():
        if m21.note.Note(n).name == minor_leading_tone:
            key_detected = possible_key_minor
            break
    return key_detected

def detect_key_by_ending_chord(df, VOICES, key_sign, minor_leading_tone, key_student,
                               possible_key_major, possible_key_minor):
    '''從寫作內容判斷調性: 看最後一個和弦'''
    ending_chord = m21.chord.Chord(df[VOICES].iloc[-1,:].values)  # end on tonic
    possible_scale_degree_major = m21.roman.romanNumeralFromChord(ending_chord, possible_key_major).scaleDegree
    possible_scale_degree_minor = m21.roman.romanNumeralFromChord(ending_chord, possible_key_minor).scaleDegree
    if possible_scale_degree_major == 1:
        key_detected = possible_key_major
    elif possible_scale_degree_minor == 1:
        key_detected = possible_key_minor
    else:
        sys.stderr.write(f"something wrong with detecting key by matching key signature {key_sign} and the ending chord {ending_chord}")
        # e.g. C大調 4聲部都停在音級3
        # 看旋律中有沒有導音升高 -> 有: 小調, 沒有: 大調. 預設大調
        key_detected = detect_key_by_melody(possible_key_major, df, VOICES, minor_leading_tone, possible_key_minor)
    
    print("The key should be", key_detected)
        
    if key_student==key_detected:
        print('The student answers a correct key:', key_student)
        key = key_student
    else:
        print(f'The student answers {key_student}, while key detected should be {key_detected}')
        key = key_detected
    
    return key

def simple_interval(original_interval):
    '''in music analysis, we distinguish perfect octave (including double-octave,...) from perfect union'''
    if original_interval.simpleName=='P1':
        if original_interval.name=='P1':
            return 'P1'
        else:
            return 'P8'
    else:
        return original_interval.simpleName
    
def post_processing(df_score, *arg):
    global WRONG_TYPE
    temp = [i for i in arg if type(i)!=type(None)]
    if len(temp)==0:
        return False, False
    
    RESULT = pd.concat(temp).reset_index(drop=True)
    RESULT['result'] = RESULT['Wrong type'].apply(lambda x:WRONG_TYPE[x])

    # Place 換成小節
    df = df_score.copy()
    df.index.name = 'Place'

    VERTICAL = RESULT[RESULT['Place type']=='Vertical']
    VERTICAL_WRONG = VERTICAL[VERTICAL['Level']=='Wrong'].set_index(['Place']).sort_index()[['Level','Place type','result', 'Voice 1', 'Voice 2']]
    VERTICAL_WARNING = VERTICAL[VERTICAL['Level']=='Warning'].set_index(['Place']).sort_index()[['Level','Place type','result', 'Voice 1', 'Voice 2']]
    VERTICAL_WRONG = pd.merge(VERTICAL_WRONG, df, how='left', on='Place')
    VERTICAL_WARNING = pd.merge(VERTICAL_WARNING, df, how='left', on='Place')

    HORIZONTAL = RESULT[RESULT['Place type']=='Horizontal']
    HORIZONTAL_WRONG = HORIZONTAL[HORIZONTAL['Level']=='Wrong'].set_index(['Place']).sort_index()[['Level','Place type','result', 'Voice 1', 'Voice 2']]
    HORIZONTAL_WARNING = HORIZONTAL[HORIZONTAL['Level']=='Warning'].set_index(['Place']).sort_index()[['Level','Place type','result', 'Voice 1', 'Voice 2']]

    ALL_RESULT = pd.concat([VERTICAL_WRONG,HORIZONTAL_WRONG,VERTICAL_WARNING,HORIZONTAL_WARNING])
    ALL_RESULT.index.name = 'Place'
    ALL_RESULT = ALL_RESULT.set_index(['Level','Place type',ALL_RESULT.index])

    return ALL_RESULT, True

def xml_to_df(xml_str):
    note_table = pd.DataFrame([], columns = ['S','A','T','B','measure', 'scale degree'])
    i = 0
    find_head = False
    info_table = pd.DataFrame([], columns = ['Time signature','Key signature','Type','Mode','Key by student', 'Lecture'])
    
    while i < len(xml_str):

        if not find_head:
            find_head = True
            # 找節拍 beat
            beat_position = xml_str[i:].find('<beats>')
            beat_position_end = xml_str[i:].find('</beats>')

            beat_type_position = xml_str[i:].find('<beat-type>')
            beat_type_position_end = xml_str[i:].find('</beat-type>')

            time_signature = xml_str[i + len('<beats>') + beat_position : i + beat_position_end] + r'/' + \
                             xml_str[i + len('<beat-type>') + beat_type_position : i + beat_type_position_end]
            info_table.loc[1, 'Time signature'] = time_signature
            
            # 找 key
            key_position = xml_str[i:].find('<fifths>')
            key_position_end = xml_str[i:].find('</fifths>')

            info_table.loc[1, 'Key signature'] = xml_str[i + len('<fifths>') + key_position : i + key_position_end]

            # 找副標
            subtitle_position = xml_str[i:].find('<credit-type>subtitle')
            
            # 如果沒有副標就跳過以下
            if subtitle_position != -1:
                type_position = xml_str[i + subtitle_position:].find('<credit-words ') + subtitle_position
                type_position_end = xml_str[i + subtitle_position:].find('</credit-words>') + subtitle_position
                # print(xml_str[i + len('<credit-words ') + type_position : i + type_position_end])
                subtitle = xml_str[i + len('<credit-words ') + type_position : i + type_position_end]
                
                # 找 Type
                student_type = subtitle.find('Type:')
                if student_type != -1:
                    student_type_end = subtitle[student_type:].find(',')
                    if student_type_end != -1:
                        info_table.loc[1, 'Type'] = subtitle[student_type + len('Type:') : student_type + student_type_end]

                # 找 Key by student
                student_key = subtitle.find('Key:')
                if student_key != -1:
                    # 看後面是否有 lecture
                    student_key_end = subtitle[student_key:].find(',')
                    if student_key_end != -1:
                        info_table.loc[1, 'Key by student'] = subtitle[student_key + len('Key:') : student_key + student_key_end]
                    else:
                        info_table.loc[1, 'Key by student'] = subtitle[student_key + len('Key:') :]
            
                # 找 Lecture
                lecture = subtitle.find('L')
                if lecture != -1:
                    info_table.loc[1, 'Lecture'] = subtitle[lecture:]

            
        # 尋找每個小節的起點
        sub_start = xml_str[i:].find('<measure number=')
        measure = xml_str[i+len('<measure number=')+sub_start+1]
        # 如果找不到就退出
        if sub_start == -1:
            break
        # 尋找每個小節的終點
        sub_end = xml_str[i+sub_start:].find('</measure>') + sub_start +len('</measure>')
        # 最後一個小節的終點不太一樣
        if sub_end == -1:
            sub_end = xml_str[i+sub_start:].find('</score-partwise>') + sub_start +len('</score-partwise>')
        # 決定處理的小節
        subsection = xml_str[i+sub_start:i+sub_end]
        j = 0
        SUB = []
        while j < len(subsection):
            # 尋找每個音域的起點
            range_start = subsection[j:].find('<note default')
            # 如果找不到就退出
            if range_start == -1:
                break
            # 尋找每個音域的終點
            range_end = subsection[j+range_start:].find('<backup>') + range_start + len('<backup>')
            # 最後一個音域的終點不太一樣
            if subsection[j+range_start:].find('<backup>') == -1:
                range_end = subsection[j+range_start:].find('</measure>') + range_start + len('</measure>')
            # 決定處理的音域
            Range = subsection[j+range_start:j+range_end]
            k = 0
            m = 0
            RANGE = []
            while k < len(Range):
                # 尋找每個音符的起點
                note_music = Range[k:].find('<step>')
                # 如果找不到就退出
                if note_music == -1:
                    break
                # 尋找每個音符的終點
                note_location = Range[k:].find('<octave>')
                alter = Range[k+note_music:k+note_location].find('<alter>')
                alter_end = Range[k+note_music:k+note_location].find('</alter>')
                if alter == -1:
                    # 沒有升降記號的讀取音符
                    note = Range[k + note_music + len('<step>')] + Range[k + note_location + len('<octave>')]
                else:
                    temp = int(Range[k + note_music + alter + len('<alter>'): k + note_music + alter_end])
                    if temp > 0:
                        temp = '#' * temp
                    else:
                        temp = '-' * abs(temp)
                    note = Range[k + note_music + len('<step>')] + temp + Range[k + note_location + len('<octave>')]
                    
#                     # 升記號
#                     if Range[k+note_music+alter+len('<alter>')] == '1':
#                         note = Range[k + note_music + len('<step>')] + '#' + Range[k + note_location + len('<octave>')]
#                     # 降記號
#                     if Range[k+note_music+alter+len('<alter>')] == '-1':
#                         note = Range[k + note_music + len('<step>')] + 'b' + Range[k + note_location + len('<octave>')]
                
                RANGE.append(note)
                m += 1
                # 決定下一個起始點
                k += note_location + len('<octave>') + 1
                
            SUB.append(RANGE)
            # 決定下一個起始點
            j += range_end + len('<backup>') + 1
            
        # 合併找到的音符
        SUB.append([measure for idx in range(m)])

        note_table = pd.concat([note_table, pd.DataFrame(np.array(SUB).T, columns = ['S','A','T','B','measure'])], ignore_index = True)
        # 決定下一個起始點
        i += sub_end
    i = 0
    Harmo = []
    while i < len(xml_str):
        harmo_start = xml_str[i:].find('<function>')
        if harmo_start == -1:
            break
        harmo_end = xml_str[i+harmo_start:].find('</function>') + harmo_start
        harmo = xml_str[i+harmo_start+len('<function>'):i+harmo_end]
        Harmo.append(harmo)
        i += harmo_end
    if Harmo:
        note_table['scale degree'] = Harmo
    
    return note_table, info_table

class Sample:    
    def __init__(self, file_path, file_path_xlsx=None):
        with open(file_path, 'r', encoding = 'utf-8') as stream:
            xml_str = stream.read()
            
        self.xml_str = xml_str
        #self.df_info = pd.read_excel(file_path_xlsx, sheet_name='Info')
        self.df_score, self.df_info = xml_to_df(xml_str)
        
    def get_info(self, show_key_sign_and_time_sign=True):
        print(f"{'-'*20}{'df_info':^10}{'-'*20}")
        
        # Required
        print("[Required]")
        time_sign = m21.meter.TimeSignature(self.df_info['Time signature'][1])
        key_sign = m21.key.KeySignature(int(self.df_info['Key signature'][1]))   # absolutely correct
        print("key signature:", key_sign)
        print("the pitches altered by this key signature:", [p.name for p in key_sign.alteredPitches]) 
        
        self.time_sign = time_sign      # music21.meter.TimeSignature: time signature given by question
        self.key_sign = key_sign        #    music21.key.KeySignature: key signature given by question
        
        if show_key_sign_and_time_sign:
            from music21 import stream
            s = stream.Stream()
            s.append(key_sign)
            s.append(time_sign)
            s.show()

        # Optional
        print("[Optional]")
        # Lecture: 單元
        lecture = self.df_info['Lecture'][1]
        if pd.isnull(lecture):
            lecture = None
        print(f"lecture: {lecture}")
        # Type: 高音題 S / 低音題 B / 無 np.nan
        question_type = self.df_info['Type'][1]  
        print(f"question_type: {question_type}")
        # Key: 題目指定大小調
        question_mode = self.df_info['Mode'][1]
        print(f"question_mode: {question_mode}")
        # Key by student: 學生自行填寫的調性
        try:
            key_student = m21.key.Key(self.df_info['Key by student'][1])  # need to check if this matches wtih key_sign and tonic_chord
            print(f"key_student: {key_student}")
        except:
            key_student = None
            print(f"key_student {key_student} is not available. set as None.")

        self.question_type = question_type  #             str: S / B / np.nan (other)
        self.question_mode = question_mode  #             str: major / minor / np.nan (other)
        self.key_student = key_student      # key.Key or None: 學生自行填寫的調性
        self.lecture = lecture
        
    def get_score(self):
        print(f"{'-'*20}{'df_score':^10}{'-'*20}")
        
        # Required: 此題有幾個聲部
        print("[Required]")
        VOICES = self.df_score.columns[:-2]
        print(f"VOICES: {VOICES}")          # order: SATB
        
        # Optional: 但應該要有 (defined by teacher)
        print("[Optional]")
        scale_degree = self.df_score['scale degree']
        print(scale_degree.isnull())
        
        self.VOICES = VOICES
        self.scale_degree = scale_degree
        
    def check_key(self):
        if pd.notna(self.question_mode):   # 題目有提供大調或小調
            try:
                key = self.key_sign.asKey(mode=self.question_mode)
            except:  # Error as err:
                #sys.stderr.write(f"something wrong with question_mode {self.question_mode}: {err}")
                # 需要從調號推測
                key = detect_key_by_key_sign(self.key_sign, self.question_type, self.VOICES,
                                             self.df_score, self.key_student)
        else:  # 從調號推測
            key = detect_key_by_key_sign(self.key_sign, self.question_type, self.VOICES,
                                         self.df_score, self.key_student)
        
        self.key = key
        self.leading_tone = key.getLeadingTone()
        self.scale = key.getScale(mode=key.mode)