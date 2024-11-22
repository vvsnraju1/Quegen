import ast
import shutil

from qna_generator import *
import re
from fastapi import FastAPI, Query
from typing import Optional, List
import pickle
from ollama_integration import *
# from TrueFalse_ollama import *
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
    
    input_path_1 = './Input/'
    output_path_1 = './Output/'
    temp_path_1 = './temp_files/'

    input_file_1 = input_file_name_1
    print("--------{}----------".format(input_file_1))

    file_name_1 = "_".join(input_file_1.split('.')[:-1])
    file_type_1 = str(input_file_1.split('.')[-1])

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
    output_path_1 = './Output/'
    temp_path_1 = './temp_files/'

    print(f"The input file name is:{input_file_name_1}")

    input_file_1 = input_file_name_1
    file_name_1 = "_".join(input_file_1.split('.')[:-1])
    print("--------{}----------".format(file_name_1))

    try:
        print('get_section_details')
        config_path = './temp_files/config_{}.pkl'.format(file_name_1)

        with open(config_path, "rb") as f:
            config = pickle.load(f)
        f.close()

        data_list = get_section_data(file_name_1, sections_to_consider, sections_to_eliminate, config['out_path_1'],config['file_type_1'])

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

            
            
            flattened_added_sentences = [sentence for sublist in new_or_modified_sentences for sentence in sublist] if isinstance(new_or_modified_sentences[0], list) else new_or_modified_sentences
            flattened_modified_sentences = [sentence for sublist in modified_or_deleted_sentences for sentence in sublist] if isinstance(modified_or_deleted_sentences[0], list) else modified_or_deleted_sentences

            message['Sentences Added/Modified'] = flattened_added_sentences
            message['Sentences Deleted/Modified'] = flattened_modified_sentences

            added_sentences = ' '.join(message['Sentences Added/Modified'])
            modified_sentences = ' '.join(message['Sentences Deleted/Modified'])
            joined_message = f"{added_sentences} {modified_sentences}"
            print(joined_message)
            '''
            # delete_temp_files(file_name_1)
            added_sentences = ' '.join(message['Sentences Added/Modified'])
            modified_sentences = ' '.join(message['Sentences Deleted/Modified'])
            joined_message = f"{added_sentences} {modified_sentences}"
            '''
            message_returned = dict()
            
            sentences = joined_message.split(". ")
            bullet_points = [f"* {sentence.strip()}" for sentence in sentences if sentence]
            
            
            #message_returned["new text"] = bullet_points
            message_returned["MCQs"] = get_mcq_question_answers(joined_message)
            message_returned["T/F Questions"] =get_true_false_questions(joined_message)
            message_returned["Short Answer Questions"]=get_saq_question_answers(joined_message)

            return message_returned 
        

        message = dict()
        #data_list = data_list[0]
        
        flattened_data_list = [item for sublist in data_list for item in sublist]

        # Join the flattened list into a single string
        joined_data = "".join(flattened_data_list)

        print(f"joined data: {joined_data}")

        # Now you can call your functions with the joined data
        message = get_mcq_question_answers(joined_data)

        # Generate True/False questions
        true_false_message = get_true_false_questions(joined_data)
        
        saq_message=get_saq_question_answers(joined_data)

        combined_message={
            **message,
            **true_false_message,
            **saq_message
        }

        return combined_message

    
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
        return {'message': 'Section names could not be extracted. Please extract the section names manually'}


def clean_text(text):
    """Remove periods from the input text and return clean text."""
    return ''.join(text.split('.'))

def get_section_data(file_name_1, sections_to_consider, sections_to_eliminate, out_path, file_type):
    print('get_section_data')
    print(f"input params: file_name_1: {file_name_1}, sections_to_consider: {sections_to_consider}, sections_to_eliminate: {sections_to_eliminate}, out_path: {out_path}, file_type: {file_type}")
    
    config_path = f'./temp_files/config_{file_name_1}.pkl'
    with open(config_path, "rb") as f:
        config = pickle.load(f)
    
    # Initialize data_list_consider as an empty list
    data_list_consider = []
    
    # Check if there are sections to consider
    if sections_to_consider and (sections_to_consider != ['None']) and (len(sections_to_consider[0]) > 5):
        sections_to_consider = sections_to_consider[0]
        sections_to_consider = ast.literal_eval(sections_to_consider)

        if not isinstance(sections_to_consider, tuple):
            sections_to_consider = [sections_to_consider]

        for i in range(len(sections_to_consider) - 1):
            section_start = sections_to_consider[i]
            section_end = sections_to_consider[i + 1]
            print(f"\nExtracting data between sections: {section_start} to {section_end}")

            # Extract the section data
            data_list_temp = extract_section_data(out_path, section_start, section_end, file_type)
            print("Raw extracted data:", data_list_temp)

            # Ensure data_list_temp is a flat list and clean it
            if isinstance(data_list_temp, list):
                # If it's a list of lists, flatten it
                flat_data_list_temp = [item for sublist in data_list_temp for item in sublist] if any(isinstance(i, list) for i in data_list_temp) else data_list_temp
            else:
                flat_data_list_temp = [data_list_temp]  # In case it's a single item
            
            # Clean each extracted item
            data_list_temp_cleaned = [clean_text(item) for item in flat_data_list_temp]  
            print("Cleaned data list temp:", data_list_temp_cleaned)
            data_list_consider.extend(data_list_temp_cleaned)

    # If no sections were considered, extract data from all sections
    if len(data_list_consider) < 1:
        print("Considering all sections")
        data_list_consider = extract_section_data(out_path, '', '', file_type)
        # Clean the data from all sections
        data_list_consider = [clean_text(item) for item in data_list_consider]
        print("Cleaned data from all sections:", data_list_consider)

    data_list_eliminate = []
    
    # Process sections to eliminate if they exist
    if sections_to_eliminate and (sections_to_eliminate != ['None']) and (len(sections_to_eliminate[0]) > 5):
        print("Inside sections to eliminate")
        sections_to_eliminate = sections_to_eliminate[0]
        sections_to_eliminate = ast.literal_eval(sections_to_eliminate)

        if not isinstance(sections_to_eliminate, tuple):
            sections_to_eliminate = [sections_to_eliminate]

        for i in range(len(sections_to_eliminate) - 1):
            start_section = sections_to_eliminate[i]
            end_section = sections_to_eliminate[i + 1]

            data_list_temp = extract_section_data(out_path, start_section, end_section, file_type)
            print("Raw extracted data for eliminate:", data_list_temp)

            # Ensure data_list_temp is flat
            if isinstance(data_list_temp, list):
                flat_data_list_temp = [item for sublist in data_list_temp for item in sublist] if any(isinstance(i, list) for i in data_list_temp) else data_list_temp
            else:
                flat_data_list_temp = [data_list_temp]

            # Clean the eliminated data
            data_list_temp_cleaned = [clean_text(item) for item in flat_data_list_temp]
            print("Cleaned data list for elimination:", data_list_temp_cleaned)
            data_list_eliminate.extend(data_list_temp_cleaned)

    print("-------------------------------------------data_list")
    # Filter out eliminated items from the considered ones
    data_list = [sent for sent in data_list_consider if sent not in data_list_eliminate]
    print("-------------------------------------------inside before returning")
    
    return data_list

def generate_questions(data_list, file_name, output_path):
    print('generate_questions')
    if data_list:
        data_list = clean_sentences(data_list)

    if data_list:
        # Generate questions
        mcq_df = get_mcq_question_answers(data_list)
        true_false_df = get_true_false_questions(data_list)
        saq_df=get_saq_question_answers(data_list)
        

        message = write_output_to_excel(file_name, output_path, saq_df, true_false_df, mcq_df)
        return message

    else:
        print("No data found")
        return {'message': 'Data not found'}
    
#new api call to return the modified text

@app.get('/get_modified_text')
def get_section_details(input_file_name_1: str,
                        sections_to_consider: Optional[List[str]] = Query(None),
                        sections_to_eliminate: Optional[List[str]] = Query(None)):
    # Paths
    input_path_1 = './Input/'
    output_path_1 = './Output/'
    temp_path_1 = './temp_files/'

    print(f"The input file name is:{input_file_name_1}")

    input_file_1 = input_file_name_1
    file_name_1 = "_".join(input_file_1.split('.')[:-1])
    print("--------{}----------".format(file_name_1))

    try:
        print('get_section_details')
        config_path = './temp_files/config_{}.pkl'.format(file_name_1)

        with open(config_path, "rb") as f:
            config = pickle.load(f)
        f.close()

        data_list = get_section_data(file_name_1, sections_to_consider, sections_to_eliminate, config['out_path_1'],config['file_type_1'])

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
 
            
            
            flattened_added_sentences = [sentence for sublist in new_or_modified_sentences for sentence in sublist] if isinstance(new_or_modified_sentences[0], list) else new_or_modified_sentences
            flattened_modified_sentences = [sentence for sublist in modified_or_deleted_sentences for sentence in sublist] if isinstance(modified_or_deleted_sentences[0], list) else modified_or_deleted_sentences

            message['Sentences Added/Modified'] = flattened_added_sentences
            message['Sentences Deleted/Modified'] = flattened_modified_sentences

            added_sentences = ' '.join(message['Sentences Added/Modified'])
            modified_sentences = ' '.join(message['Sentences Deleted/Modified'])
            joined_message = f"{added_sentences} {modified_sentences}"
            sentences = joined_message.split(". ")
            bullet_points = [f"* {sentence.strip()}" for sentence in sentences if sentence]

            message_returned = dict()
            message_returned["Modified Text: "] = bullet_points
            message_returned['Sentences Added/Modified'] = flattened_added_sentences
            message_returned['Sentences Deleted/Modified'] = flattened_modified_sentences

            return message_returned 
        

    except (TypeError, ValueError, AttributeError, Exception) as e:
        print(f"Exception occurred: {e}")
        return {'message': 'Questions could not be generated'}




#import uvicorn  
if __name__ == "__main__":
    import uvicorn 
    uvicorn.run(app, host="127.0.0.1", port=8000)