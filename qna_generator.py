from helper import *

import pandas as pd
import base64
import os
import json


def extract_text(file_type, file_path, file_name, temp_path, watermark):
    print('extract_text')
    # ****************************** PDF ******************************
    data = ''
    if file_type == 'pdf':

        classifier_result = pdf_image_or_text(file_path)
        if 0 in classifier_result:
            print('Convert PDF to images')
            if not os.path.exists(temp_path):
                os.makedirs(temp_path)
                image_counter = convert_pdf_to_images(file_path, temp_path)

            out_path = temp_path + 'output_text.txt'

            if watermark:
                print("Removing watermark and extracting text from the images")
                images = [i for i in os.listdir(temp_path) if '.jpg' in i]
                for image in images:
                    image_path = temp_path + image
                    remove_watermark(filename=image_path, out_path=out_path)

                file_object = open(out_path, "r", encoding="utf8")
                data = file_object.read()
                file_object.close( )

            elif 'output_text.txt' not in os.listdir(temp_path):
                print('Extracting text from images')
                image_counter = len(os.listdir(temp_path))
                data = ocr(image_counter, temp_path, out_path)

        else:
            if not os.path.exists(temp_path):
                os.makedirs(temp_path)

            print('Extracting text from PDF')
            out_path = temp_path + 'output_text.txt'
            if 'output_text.txt' not in os.listdir(temp_path):
                data = gettext_from_pdf(file_path, out_path)

    # ****************************** docx ******************************
    elif file_type == 'docx':
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)

        print('Extracting text from docx')
        out_path = temp_path + 'output_text.txt'

        if 'output_text.txt' not in os.listdir(temp_path):
            data = gettext_from_docx(file_path, temp_path, file_name, out_path)

    # ****************************** pptx ******************************
    elif file_type == 'pptx':
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)

        print('Extracting text from pptx')
        out_path = temp_path + 'output_text.txt'

        if 'output_text.txt' not in os.listdir(temp_path):
            data = gettext_from_pptx(file_path, out_path)

    # ****************************** base64 PDF ******************************
    elif file_type == 'txt':
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)

        print('Extracting text from base64')
        with open(file_path, "rb") as f:
            text = f.read()
        f.close()

        pdf_path = temp_path + file_name + ".pdf"

        with open(pdf_path, "wb") as f:
            f.write(base64.b64decode(text))
        f.close()

        out_path = temp_path + 'output_text.txt'

        if 'output_text.txt' not in os.listdir(temp_path):
            data = gettext_from_pdf(pdf_path, out_path)

    return data


def mcq_generator(data_list):
    print('mcq_generator')
    # ****************************** MCQ questions ******************************
    mcq_list = generate_mcq(data_list)
    mcq_list = [[lst[0], lst[1][0], lst[1][1], lst[1][2], lst[1][3], lst[2], lst[3]] for lst in mcq_list if
                len(lst[1]) == 4]
    mcq_df = pd.DataFrame.from_records(mcq_list).reset_index()
    try:
        mcq_df.columns = ['SNo', 'Question', 'OptionA', 'OptionB', 'OptionC', 'OptionD', 'Answer', 'Question Context']
    except ValueError:
        return {'message': 'No MCQ questions generated'}
    mcq_df['SNo'] = mcq_df['SNo'] + 1

    answer_list = list()
    for _, row in mcq_df.iterrows():
        val = row[row == row['Answer']].index
        answer_list.append(val[0])
    mcq_df['Answer'] = answer_list
    return mcq_df


def true_false_generator(data_list):
    print('true_false_generator')
    # ****************************** True/False questions ******************************
    true_false_list = generate_true_false_questions(data_list)
    true_false_df = pd.DataFrame.from_records(true_false_list).reset_index()
    try:
        true_false_df.columns = ['SNo', 'Question', 'Answer', 'Question Context']
    except ValueError:
        return {'message': 'No True/False questions generated'}
    true_false_df['SNo'] = true_false_df['SNo'] + 1
    return true_false_df

def saq_generator(data_list):
    print('saq_generator')
    # ****************************** True/False questions ******************************
    saq_list = generate_saq(data_list)
    saq_df = pd.DataFrame.from_records(saq_list).reset_index()
    try:
        saq_df.columns = ['SNo', 'Question', 'Answer', 'Question Context']
    except ValueError:
        return {'message': 'No True/False questions generated'}
    saq_df['SNo'] = saq_df['SNo'] + 1
    return saq_df


def write_output_to_excel(file_name, output_path, saq_df,true_false_df, mcq_df):
    print('write_output_to_excel')
    # ****************************** Write to file ******************************
    file_name_excel = file_name + '.xlsx'
    out_file_path = output_path + file_name_excel

    message_dict = dict()
    try:
        with pd.ExcelWriter(out_file_path) as writer:
            mcq_df.to_excel(writer, sheet_name='MCQ Questions', index=None)
        mcq_json = mcq_df.to_json(orient='records')
        message_dict['MCQ_questions'] = json.loads(mcq_json)
    except AttributeError:
        print("Not enough data to generate MCQ questions")

    try:
        with pd.ExcelWriter(out_file_path, engine="openpyxl", mode='a') as writer:
            true_false_df.to_excel(writer, sheet_name='TrueFalse Questions', index=None)
        true_false_json = true_false_df.to_json(orient='records')
        message_dict['true_false_questions'] = json.loads(true_false_json)
    except AttributeError:
        print("Not enough data to generate True/False questions")
        
    try:
        with pd.ExcelWriter(out_file_path, engine="openpyxl", mode='a') as writer:
            saq_df.to_excel(writer, sheet_name='SAQ Questions', index=None)
        saq_json = saq_df.to_json(orient='records')
        message_dict['SAQ_questions'] = json.loads(saq_json)
    except AttributeError:
        print("Not enough data to generate SAQ  questions")

    print("Question and answers have been generated and saved at: {}".format(out_file_path))
    print("---------------- Process finished for file {} --------------".format(file_name))
    if len(message_dict) < 1:
        return {'message': 'Not enough data to generate questions'}
    return message_dict
