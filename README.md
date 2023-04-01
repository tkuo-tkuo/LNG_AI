# LNG_AI
Automatically generate LNG-like contents based on LNG streaming data

# Non-Technical
- [ ] Get buy-in with LNG members
- [ ] Select & add appropriate license
- [ ] Include overall design chart
- [ ] Include references
- [ ] Add what dataset structures should look like in README
- [ ] Don't directly store data on GitHub repository for faster pull/push speed, leaving link to zip file or instructions instead

# Technical 

## Setup  
- [x] Support conda environment reconstruction

Create your environment by conda
```bash
$ conda env create -f environment.yml
$ conda activate lng_ai
```

Create `.env` and place your keys within like
```bash
export yt_api_key=...
export OPENAI_API_KEY=...
```

## Data Collection & Parsing 
- [x] Download audio files with its original video informations (e.g., title, URL, and publish date)
- [x] Transcribe based on audio files (e.g., Whisper), see more details in [candidates evaluation](transcribe_candidates.md)
- [x] Convert transcript into prompt/completion JSONL training dataset ([OpenAI dataset preparation](https://platform.openai.com/docs/guides/fine-tuning/preparing-your-dataset))
- [x] Add checker to verify data integrity for all audio/transcript format

**Download audio files**

```bash
$ python3 download_audio_files.py 
```
Results will be stored in tables with two formats supported, default paths are `audio_infos.md` and `audio_infos.csv`

**Transcribe audio files**

```bash
$ python3 transcribe_audio_files.py 
```

**Make jsonl dataset based on transcripts (0.1 threshold used)**

```bash
$ python3 prepare_dataset.py --repetitive_word_threshold 0.1
```

Note that even we leverage OpenAI Whisper to transcribe from audio to transcripts, some results of transcripts seem problematic (same word occur repetitively). 

Hence we have a mechanism to filter out transcripts that have certain word occurs more than given threshold (e.g., 10%). 

For instance, if a word "哈哈" appears 18% in the transcript, this transcript will be excluded in the training dataset if threshold is 10% (not excluded if threshold is 20%).

| Threshold | Remaining Dataset Size | Remaining % |
| --- | --- | --- |
| 0.01 | 632 | 0.95 |
| 0.05 | 49567 | 74.71 |
| 0.1 | 60033 | 90.48 |
| 0.25 | 64292 | 96.9 |
| 0.5 | 65148 | 98.19 |

## Model Training
- [x] Select & download suitable LLM (fine-tuned [Babbage model](https://openai.com/pricing) by OpenAI)
- [x] Fine-tune by LNG data

**Fine-tune from scratch**

```bash
$ python3 fine_tune_openai_model.py --mode 0 --jsonl_dataset_path $JSONL_DATASET_PATH
$ python3 fine_tune_openai_model.py --mode 0 --jsonl_dataset_path jsonl_dataset/jsonl_dataset_50_percent_29608.jsonl
```

**View fine-tune models (include corresponding training history)**

```bash
$ python3 fine_tune_openai_model.py --mode 1
```

**Test fine-tune models**

```bash
$ python3 fine_tune_openai_model.py --mode 2 --model_name $MODEL_NAME --num_of_sentences_generated $NUM_OF_SENTENCES_GENERATED
$ python3 fine_tune_openai_model.py --mode 2 --model_name babbage:ft-personal-2023-03-31-16-53-00 --num_of_sentences_generated 10
```

**View training process**

```bash
$  python3 fine_tune_openai_model.py --mode 3 --model_id $MODEL_ID
$  python3 fine_tune_openai_model.py --mode 3 --model_id $ft-YYivAE5wK5tEGjKhJblhimCq
```

- [ ] Manually verify results & gradually improve

## Provide user-friendly UI for public
- [ ] Developer & construct website locally
- [ ] Deploy on cloud
- [ ] Address performance issue if any 