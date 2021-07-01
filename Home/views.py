from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
sbert = SentenceTransformer('/home/dung/PycharmProjects/Web_TrafficLaw/output')

from django.http import HttpResponse
from django.shortcuts import render
import numpy as np
import tensorflow as tf
import transformers
from elasticsearch import Elasticsearch
import numpy as np
import speech_recognition as sr
from gtts import gTTS
import playsound


selection = "BERT"
input = ""
output= ""
rec = []

max_length = 128  # Maximum length of input sentence to the model.
batch_size = 32
labels = ["0", "1"]


class BertSemanticDataGenerator(tf.keras.utils.Sequence):
    """Generates batches of data.
    Args:
        sentence_pairs: Array of premise and hypothesis input sentences.
        labels: Array of labels.
        batch_size: Integer batch size.
        shuffle: boolean, whether to shuffle the data.
        include_targets: boolean, whether to incude the labels.

    Returns:
        Tuples `([input_ids, attention_mask, `token_type_ids], labels)`
        (or just `[input_ids, attention_mask, `token_type_ids]`
         if `include_targets=False`)
    """

    def __init__(
        self,
        sentence_pairs,
        labels,
        batch_size=batch_size,
        shuffle=True,
        include_targets=True,
    ):
        self.sentence_pairs = sentence_pairs
        self.labels = labels
        self.shuffle = shuffle
        self.batch_size = batch_size
        self.include_targets = include_targets
        # Load our BERT Tokenizer to encode the text.
        # We will use base-base-uncased pretrained model.
        self.tokenizer = transformers.BertTokenizer.from_pretrained(
            "bert-base-uncased", do_lower_case=True
        )
        self.indexes = np.arange(len(self.sentence_pairs))
        self.on_epoch_end()

    def __len__(self):
        # Denotes the number of batches per epoch.
        return len(self.sentence_pairs) // self.batch_size

    def __getitem__(self, idx):
        # Retrieves the batch of index.
        indexes = self.indexes[idx * self.batch_size : (idx + 1) * self.batch_size]
        sentence_pairs = self.sentence_pairs[indexes]

        # With BERT tokenizer's batch_encode_plus batch of both the sentences are
        # encoded together and separated by [SEP] token.
        encoded = self.tokenizer.batch_encode_plus(
            sentence_pairs.tolist(),
            add_special_tokens=True,
            max_length=max_length,
            return_attention_mask=True,
            return_token_type_ids=True,
            pad_to_max_length=True,
            return_tensors="tf",
        )

        # Convert batch of encoded features to numpy array.
        input_ids = np.array(encoded["input_ids"], dtype="int32")
        attention_masks = np.array(encoded["attention_mask"], dtype="int32")
        token_type_ids = np.array(encoded["token_type_ids"], dtype="int32")

        # Set to true if data generator is used for training/validation.
        if self.include_targets:
            labels = np.array(self.labels[indexes], dtype="int32")
            return [input_ids, attention_masks, token_type_ids], labels
        else:
            return [input_ids, attention_masks, token_type_ids]

    def on_epoch_end(self):
        # Shuffle indexes after each epoch if shuffle is set to True.
        if self.shuffle:
            np.random.RandomState(42).shuffle(self.indexes)


# Create the model under a distribution strategy scope.
strategy = tf.distribute.MirroredStrategy()

with strategy.scope():
    # Encoded token ids from BERT tokenizer.
    input_ids = tf.keras.layers.Input(
        shape=(max_length,), dtype=tf.int32, name="input_ids"
    )
    # Attention masks indicates to the model which tokens should be attended to.
    attention_masks = tf.keras.layers.Input(
        shape=(max_length,), dtype=tf.int32, name="attention_masks"
    )
    # Token type ids are binary masks identifying different sequences in the model.
    token_type_ids = tf.keras.layers.Input(
        shape=(max_length,), dtype=tf.int32, name="token_type_ids"
    )
    # Loading pretrained BERT model.
    bert_model = transformers.TFBertModel.from_pretrained("bert-base-uncased")
    # Freeze the BERT model to reuse the pretrained features without modifying them.
    bert_model.trainable = False

    sequence_output, pooled_output = bert_model(
        input_ids, attention_mask=attention_masks, token_type_ids=token_type_ids
    )
    # Add trainable layers on top of frozen layers to adapt the pretrained features on the new data.
    bi_lstm = tf.keras.layers.Bidirectional(
        tf.keras.layers.LSTM(64, return_sequences=True)
    )(sequence_output)
    # Applying hybrid pooling approach to bi_lstm sequence output.
    avg_pool = tf.keras.layers.GlobalAveragePooling1D()(bi_lstm)
    max_pool = tf.keras.layers.GlobalMaxPooling1D()(bi_lstm)
    concat = tf.keras.layers.concatenate([avg_pool, max_pool])
    dropout = tf.keras.layers.Dropout(0.3)(concat)
    output = tf.keras.layers.Dense(3, activation="softmax")(dropout)
    model = tf.keras.models.Model(
        inputs=[input_ids, attention_masks, token_type_ids], outputs=output
    )
    model1=tf.keras.models.Model(inputs=[input_ids, attention_masks, token_type_ids], outputs=output
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(),
        loss="categorical_crossentropy",
        metrics=["acc"],
    )

# print(f"Strategy: {strategy}")
model.summary()

model.load_weights("/home/dung/PycharmProjects/Web_TrafficLaw/Home/weights3.h5")


def check_similarity(sentence1, sentence2):
    sentence_pairs = np.array([[sentence1,sentence2]])
    test_data = BertSemanticDataGenerator(
        sentence_pairs, labels=None, batch_size=1, shuffle=False, include_targets=False,
    )

    proba = model.predict(test_data)[0]
    idx = np.argmax(proba)
    # proba = f"{proba[idx]: .2f}%"
    proba = proba[idx]
    pred = labels[idx]
    return pred, proba


def similarity_sentence(sents):

    sentence_embeddings = sbert.encode(sents)
    similarites = cosine_similarity(sentence_embeddings)
    similarites_sorted = similarites.argsort()
    id_1 = []
    id_2 = []
    score = []
    array = similarites_sorted[0]
    for idx, val in enumerate(array):
        id_1.append(0)
        id_2.append(val)
        score.append(similarites[0][val])
    return sents[id_2[-2]], similarites[0][array[-2]]

def PhoBert_Semantic(input,list):

    sents = []
    sents.append(input)
    print(list)
    for i in range(0,3):
        sents.append(list[i][0])

    s2,score = similarity_sentence(sents)

    return s2,score

def search_answer(s):
    es = Elasticsearch('http://192.168.43.110:9200')

    es.indices.refresh(index="qaluat")
    # res = es.search(index="qaluat", body={"query": {"match": {'question': s}}})
    res = es.search(index="qaluat", body={"query": {"bool": {"must": {"match": {'question': s}}}}}, size=1)

    for hit in res['hits']['hits']:
       out = hit["_source"]['answer']
       return out



def search_qaluat2(s):
      sentences = []
      print(s+'############################################################')

      es = Elasticsearch('http://192.168.43.110:9200')

      es.indices.refresh(index="qaluat2")
      # res = es.search(index="qaluat2", body={"query": {"match": {'question': s}}})
      res = es.search(index="qaluat2", body={"query": {"bool": {"must": {"match": {'question': s}}}}}, size=20)
      i = 0

      for hit in res['hits']['hits']:
          #sentences.append([])
          q = hit["_source"]['question']
          print(q)

          if str(q) == str(s):
            ss = hit["_source"]['answer']
            ss1 =" "+search_answer(ss)
              # sentences[i].append(s)
            sentences.append(ss1)

            print(ss1 + '############################################################')
            i+=1
      return sentences

def search_elasticsearch(s):
      sentences = [[]]

      es = Elasticsearch('http://192.168.43.110:9200')

      es.indices.refresh(index="qaluat")
      # res = es.search(index="qaluat", body={"query": {"match": {'question': s}}})
      res = es.search(index="qaluat", body={"query": {"bool": {"must": {"match": {'question': s}}}}}, size=5)
      i = 0
      for hit in res['hits']['hits']:

          sentences.append([])
          sentences[i].append(hit["_source"]['question'])
          sentences[i].append(hit["_source"]['answer'])
          i = i + 1

      return sentences


def speechToText(request):

    input=""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        # text1 = "Mời bạn hỏi"
        # output1 = gTTS(text1, lang="vi", slow=False)
        # output1.save("output.mp3")
        # playsound.playsound('output.mp3', True)
        audio = r.listen(source, phrase_time_limit=6)
        try:
            text = r.recognize_google(audio, language="vi-VI")
            input = text
            print("{}".format(text))
            output1 = gTTS(text, lang="vi", slow=False)
            output1.save("output.mp3")
            playsound.playsound('output.mp3', True)
        except:
            text2 = "Xin lỗi tôi không nghe thấy bạn nói gì!"
            output2 = gTTS(text2, lang="vi", slow=False)
            output2.save("output.mp3")
            playsound.playsound('output.mp3', True)

    content={
        'question': input,
        'select': selection,
        'answer': '',
        'recommend': rec,
    }
    return render(request,'pages/process.html',content)

def textToSpeech(request):

    text = "Không có gì cả"
    output = request.POST["ans"]
    if str(output) != "":
        text = output
    else:
        text = "Không có gì cạ"

    output2 = gTTS(text, lang="vi", slow=False)
    output2.save("output.mp3")
    playsound.playsound('output.mp3', True)

    content = {
        'question': input,
        'select': selection,
        'answer': output,
        'recommend': rec,
    }
    return render(request, 'pages/process.html', content)

def process(request):

    input = request.POST['question']
    selection = request.POST['select']
    try:
        new_ques = request.POST['rec_question']
    except:
        new_ques = input

    rec=[]
    list = search_elasticsearch(input)
    max = 0
    for i in range(0,5):
        rec.append(list[i][0])

    output = 'Không có kết quả'
    if selection=='BERT':
        for i in range(0,3):
            label, acc = check_similarity(input, str(list[i][0]))
            if label == '1' and acc >= max:
                max = acc
                output = str(list[i][1])
    # else:
    #     s,max = PhoBert_Semantic(input,list)
    #     output = search_answer(s)
    #     print(s)
    #     print(output)
    for i in range(0, 3):
        label, acc = check_similarity(input, str(list[i][0]))
        if label == '1' and acc >= max:
            max = acc
            output = str(list[i][1])
    sentences = search_qaluat2(output)

    content={
        'question': input,
        'select': selection,
        'answer': output,
        'recommend': rec,
        'sentences': sentences,

    }


    return render(request,'pages/process.html',content)

def home(request):

    rec1 = 'Mời bạn nhập nội dung vào đây, mỗi lần enter xuống dòng là hết 1 câu nha!'
    rec2 = 'Lựa chọn model ở trên này nha'
    rec3 = 'Chưa có nội dung hiển thị'
    list_rec = []
    content ={
        'holder': rec1,
        'select': rec2,
        'recommend': rec3,
        'list': list_rec,
    }
    template_name = 'pages/home.html'
    return render(request, template_name, content)



