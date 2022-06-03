#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  1 00:12:22 2022

@author: clarelin
"""
import pandas as pd

class Harmony_checker:
    def __init__(self, file_path):
        from basic_information import Sample
        
        y = Sample(file_path)
        y.get_info()
        y.get_score()
        y.check_key()       
        self.y = y
        
    def run(self):
        # Read Data    
        # 1. 音域方面
        from detection_1_related_to_voice import vocal_range_detection, spacing_detection,\
                                                 voice_crossing_detection, overlapping_detection
        
        vocal_range_detector = vocal_range_detection(self.y.VOICES, self.y.df_score)        # 個別音域 (Vocal Range)
        spacing_detector = spacing_detection(self.y.VOICES, self.y.df_score)                # 配置 (Spacing)
        voice_crossing_detector = voice_crossing_detection(self.y.VOICES, self.y.df_score)  # 交越 (Voice Crossing)
        overlapping_detector = overlapping_detection(self.y.VOICES, self.y.df_score)        # 越位 (Overlapping)
        
        # 2. 旋律方面
        from detection_2_related_to_melody import melody_interval_detection, melody_jump_detection,\
                                                  leading_tone_resolution_detection, leading_tone_minor_detection
        
        # 單一聲部橫向進行不可有增減音程, A4,d5 除外
        melody_interval_detector = melody_interval_detection(self.y.VOICES, self.y.df_score, self.y.key, self.y.leading_tone)
        # 大跳後需反向級進或小跳
        jump_detector = melody_jump_detection(self.y.VOICES, self.y.df_score)
        # 導音處理：外聲部導音要到主音
        leading_tone_resolution = leading_tone_resolution_detection(self.y.VOICES, self.y.df_score,self.y.key, self.y.leading_tone)
        # 小調導音升高
        leading_tone_minor = leading_tone_minor_detection(self.y.VOICES, self.y.df_score, self.y.key, self.y.leading_tone)
        
        # 3. 和聲方面
        from detection_3_related_to_harmony import vertical_harmonic_related, harmony_error_detection
        
        df = vertical_harmonic_related(self.y.VOICES, self.y.df_score, self.y.key, self.y.lecture, self.y.leading_tone)
        harmony_error_detector = harmony_error_detection(df, self.y.lecture)
        
        # 4. 平行與隱伏
        from detection_4_related_to_parallel_and_hidden import parallel_and_hidden_detection
        
        parallel_and_hidden = parallel_and_hidden_detection(self.y.VOICES, self.y.df_score)
        
        # Post processing
        from basic_information import post_processing
        
        ALL_RESULT,output_flag = post_processing(self.y.df_score, vocal_range_detector, spacing_detector, voice_crossing_detector, overlapping_detector,
                                     melody_interval_detector, jump_detector, parallel_and_hidden, harmony_error_detector, leading_tone_resolution,
                                     leading_tone_minor)
        
        self.vocal_range_detector = vocal_range_detector
        self.spacing_detector = spacing_detector
        self.voice_crossing_detector = voice_crossing_detector
        self.overlapping_detector = overlapping_detector
        self.melody_interval_detector = melody_interval_detector
        self.jump_detector = jump_detector
        self.parallel_and_hidden = parallel_and_hidden
        self.harmony_error_df = df
        self.harmony_error_detector = harmony_error_detector
        self.leading_tone_resolution = leading_tone_resolution
        self.leading_tone_minor = leading_tone_minor
        self.ALL_RESULT = ALL_RESULT
        self.output_flag = output_flag
        
    def output(self, file_output_path):
        if self.output_flag:
            writer = pd.ExcelWriter(file_output_path, engine='xlsxwriter')
            self.ALL_RESULT.to_excel(writer, sheet_name='result')
            self.harmony_error_df.to_excel(writer, sheet_name='harmony detection')
            writer.save()
            