# LNG_AI
*Note: still under construction as personal habit, see [TODOs](asset/todos.md).*

Automatically generate LNG-like contents based on LNG streaming data ([version 1 demo](asset/v1_50_sentences_demo.txt))

# How to Use?
*Note: if any procedures unclear, feel free to raise an issue and ping me!*

1. Setup Environment
```shell
# Create your environment by conda
$ conda env create -f environment.yml
$ conda activate lng_ai
```  
```shell
# Create `.env` and place your keys within like
export yt_api_key=...
export OPENAI_API_KEY=...
``` 

2. Prepare data (download [zip file](https://drive.google.com/file/d/1qNNXQJwcoYS5bz-7EYe0hsVbK8r2X1yD/view?usp=sharing) or execute below commands)
```shell
$ python3 download_audio_files.py 
$ python3 transcribe_audio_files.py 
$ python3 prepare_dataset.py --repetitive_word_threshold 0.1
```

3. Model Training & Interaction
```bash
# Fine-tune from scratch
$ python3 fine_tune_openai_model.py --mode 0 --jsonl_dataset_path $JSONL_DATASET_PATH
$ python3 fine_tune_openai_model.py --mode 0 --jsonl_dataset_path jsonl_dataset/jsonl_dataset_50_percent_29608.jsonl
```

```bash
# View fine-tune models (include corresponding training history)
$ python3 fine_tune_openai_model.py --mode 1
```

```bash
# Test fine-tune models
$ python3 fine_tune_openai_model.py --mode 2 --model_name $MODEL_NAME --num_of_sentences_generated $NUM_OF_SENTENCES_GENERATED
$ python3 fine_tune_openai_model.py --mode 2 --model_name babbage:ft-personal-2023-03-31-16-53-00 --num_of_sentences_generated 10
```

```bash
# View training process
$  python3 fine_tune_openai_model.py --mode 3 --model_id $MODEL_ID
$  python3 fine_tune_openai_model.py --mode 3 --model_id $ft-YYivAE5wK5tEGjKhJblhimCq
```


# Development Milestones 
### **Version 1**

**Features**
- Download audio files via Youtube Data API
- Transcribe audio into transcripts via OpenAI Whisper API ([candidates evaluation](asset/transcribe_candidates.md))
- Process transcripts into valid JSONL training dataset ([OpenAI dataset preparation](https://platform.openai.com/docs/guides/fine-tuning/preparing-your-dataset))
- Add checker to verify data integrity of training dataset
- Train OpenAI fine-tuned model
- Interact and verify results given by fine-tuned model 

**Notes**  
Dataset Preparation Tricks
- Filter out transcrirpts that have over-reptitive word (e.g., >10%)
  - For instance, if a word "哈哈" appears 18% in the transcript, this transcript will be excluded in the training dataset.
  - Note that we leverage OpenAI Whisper to transcribe, some transcripts transcribed could be problematic (repetitive words).
- Use more than 1 sentences (e.g., 3) in prompt to make chat completion more coherent

Model
- 1-year data (2022-2023)
- 4 iterations fine-tuning
- OpenAI Baddage model 