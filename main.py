import ast
import shutil

from qna_generator import *
import re
from fastapi import FastAPI, Query
from typing import Optional, List
import pickle
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from ollama_integration import *
from a2wsgi import ASGIMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,    allow_origins=origins,    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
wsgi_app = ASGIMiddleware(app)


@app.get('/get_paths')
def get_data_paths(input_file_name_1: str, input_file_name_2: Optional[str] = None,
                   contains_watermark: bool = False):
    print("get_data_paths")
    config = dict()
    config['updated_file'] = False

    # Paths
    input_path_1 = './Input/'
    output_path_1 = './Output/'
    temp_path_1 = './temp_files/'

    input_file_1 = input_file_name_1
    print("--------{}----------".format(input_file_1))

    # Identify the file type
    file_name_1 = "_".join(input_file_1.split('.')[:-1])
    file_type_1 = str(input_file_1.split('.')[-1])

    # Generate paths to save files
    file_path_1 = input_path_1 + input_file_1
    temp_path_1 = temp_path_1 + 'temp_files_' + file_name_1 + '/'
    out_path_1 = temp_path_1 + 'output_text.txt'
    if os.path.exists(temp_path_1):
        delete_temp_files(file_name_1)

    if not os.path.exists(file_path_1):
        raise file_not_found(file_path_1)

    if file_type_1 not in ['pdf', 'txt', 'docx', 'pptx']:
        raise unidentified_filetype(file_type_1)

    config['input_file_1'] = input_file_1
    config['file_name_1'] = file_name_1
    config['file_type_1'] = file_type_1
    config['file_path_1'] = file_path_1
    config['temp_path_1'] = temp_path_1
    config['out_path_1'] = out_path_1
    config['output_path_1'] = output_path_1

    sections_list = get_section_names(file_type_1, file_path_1, file_name_1, temp_path_1,
                                      watermark=contains_watermark)

    if input_file_name_2:
        # Paths
        input_path_2 = './Input/'
        output_path_2 = './Output/'
        temp_path_2 = './temp_files/'

        input_file_2 = input_file_name_2
        print("--------{}----------".format(input_file_2))

        # Identify the file type
        file_name_2 = "_".join(input_file_2.split('.')[:-1])
        file_type_2 = str(input_file_2.split('.')[-1])

        # Generate paths to save files
        file_path_2 = input_path_2 + input_file_2
        temp_path_2 = temp_path_2 + 'temp_files_' + file_name_2 + '/'
        out_path_2 = temp_path_2 + 'output_text.txt'
        if os.path.exists(temp_path_2):
            delete_temp_files(file_name_2)

        config['updated_file'] = True
        config['input_file_2'] = input_file_2
        config['file_name_2'] = file_name_2
        config['file_type_2'] = file_type_2
        config['file_path_2'] = file_path_2
        config['temp_path_2'] = temp_path_2
        config['out_path_2'] = out_path_2
        config['output_path_2'] = output_path_2

        sections_list = get_section_names(file_type_2, file_path_2, file_name_2, temp_path_2,
                                          watermark=contains_watermark)

    config_path = './temp_files/config_{}.pkl'.format(file_name_1)
    config_path = './temp_files/config_{}.pkl'.format(file_name_1)

    with open(config_path, 'wb') as f_1:
        pickle.dump(config, f_1, protocol=pickle.HIGHEST_PROTOCOL)
    f_1.close()

    if len(sections_list) < 2:
        return {'message': 'Section names could not be extracted. Please input the section names manually'}

    return {'section_names': sections_list}


@app.get('/get_sections')
def get_section_details(input_file_name_1: str,
                        sections_to_consider: Optional[List[str]] = Query(None),
                        sections_to_eliminate: Optional[List[str]] = Query(None)):
    # Paths
    input_path_1 = './Input/'
    output_path_1 = './NewOutput/'
    temp_path_1 = './temp_files/'

    input_file_1 = input_file_name_1
    file_name_1 = "_".join(input_file_1.split('.')[:-1])
    print("--------{}----------".format(file_name_1))

    try:
        print('get_section_details')
        config_path = './temp_files/config_{}.pkl'.format(file_name_1)

        with open(config_path, "rb") as f:
            config = pickle.load(f)
        f.close()

        data_list = get_section_data(file_name_1, sections_to_consider, sections_to_eliminate, config['out_path_1'],
                                     config['file_type_1'])

        print('--------------------data for new file extracted-----------------------')
        print(data_list)

        if config['updated_file']:
            data_list_old_file = get_section_data(file_name_1, sections_to_consider, sections_to_eliminate,
                                                  config['out_path_2'],
                                                  config['file_type_2'])

            print('--------------------data for old file extracted-----------------------')
            print(data_list_old_file)

            new_or_modified_sentences = list()
            for sent in data_list:
                print('-----------------', sent, '---------')
                scores_list = list()
                for old_sent in data_list_old_file:
                    print("-------------------", old_sent)
                    score = fuzz.partial_ratio(sent, old_sent)
                    scores_list.append(score)
                if max(scores_list) < 95:
                    new_or_modified_sentences.append(sent)

            modified_or_deleted_sentences = list()
            for old_sent in data_list_old_file:
                scores_list = list()
                for sent in data_list:
                    score = fuzz.partial_ratio(old_sent, sent)
                    scores_list.append(score)
                if max(scores_list) < 95:
                    modified_or_deleted_sentences.append(old_sent)

            message = generate_questions(new_or_modified_sentences, config['file_name_1'], config['output_path_1'])
            message['Sentences Added/Modified'] = new_or_modified_sentences
            message['Sentences Deleted/Modified'] = modified_or_deleted_sentences

            # delete_temp_files(file_name_1)
            return message

        message=get_mcq_question_answers(".".join(data_list))
        #message = generate_questions(data_list, config['file_name_1'], config['output_path_1'])

        # delete_temp_files(file_name_1)
        return message

    except (TypeError, ValueError, AttributeError, Exception) as e:
        print(f"Exception occurred: {e}")
        return {'message': 'Questions could not be generated'}


def delete_temp_files(filename=None):
    path = './temp_files'
    if filename:
        path = './temp_files/temp_files_' + str(filename)
        print(path)

    for root, dirs, files in os.walk(path):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))

    if filename:
        try:
            print(path)
            os.rmdir(path)
        except (OSError, Exception) as e:
            print(f'-------------Error deleting file: {e}---------')


def get_section_names(file_type, file_path, file_name, temp_path, watermark):
    try:
        print('get_section_names')
        data = extract_text(file_type, file_path, file_name, temp_path, watermark)
        if(file_type == 'docx'):
            pattern =r"(?:[.\d]+\t?)?([a-zA-Z &/-]+)(?:[\t\d]+)?"
            sections_list = re.findall(pattern, data)
        else:
            sections_list = extract_section_names(data)
        sections_list = [i.strip() for i in sections_list]
        return sections_list
    except (ValueError, AttributeError, TypeError, Exception) as e:
        print(e)
        return {'message': 'Section names could not be extracted. Please extract the section names manually '}


def get_section_data(file_name_1, sections_to_consider, sections_to_eliminate, out_path, file_type):
    print('get_section_data')
    config_path = './temp_files/config_{}.pkl'.format(file_name_1)
    with open(config_path, "rb") as f:
        config = pickle.load(f)
    f.close()

    data_list_consider = list()
    if sections_to_consider and (sections_to_consider != ['None']) and (len(sections_to_consider[0]) > 5):
        sections_to_consider = sections_to_consider[0]
        sections_to_consider = ast.literal_eval(sections_to_consider)

        if not isinstance(sections_to_consider, tuple):
            sections_to_consider = [sections_to_consider]

        for section in sections_to_consider:
            data_list_temp = extract_section_data(out_path, section[0], section[1], file_type)
            print(data_list_temp)
            data_list_consider.extend(data_list_temp)

    if len(data_list_consider) < 1:
        print("Considering all sections")
        data_list_consider = extract_section_data(out_path, '', '', file_type)

    data_list_eliminate = list()
    if sections_to_eliminate and (sections_to_eliminate != ['None']) and (len(sections_to_eliminate[0]) > 5):
        print("Inside sections to eliminate")
        sections_to_eliminate = sections_to_eliminate[0]
        sections_to_eliminate = ast.literal_eval(sections_to_eliminate)

        if not isinstance(sections_to_eliminate, tuple):
            sections_to_eliminate = [sections_to_eliminate]

        for section in sections_to_eliminate:
            data_list_temp = extract_section_data(out_path, section[0], section[1], file_type)
            data_list_eliminate.extend(data_list_temp)

    print("-------------------------------------------data_list")
    data_list = [sent for sent in data_list_consider if sent not in data_list_eliminate]
    print("-------------------------------------------inside before returning")
    return data_list


def generate_questions(data_list, file_name, output_path):
    print('generate_questions')
    if data_list:
        data_list = clean_sentences(data_list)

    if data_list:
        # Generate questions
        mcq_df = mcq_generator(data_list)
        true_false_df = true_false_generator(data_list)

        # Write the output
        message = write_output_to_excel(file_name, output_path, true_false_df, mcq_df)
        return message

    else:
        print("No data found")
        return {'message': 'Data not found'}
