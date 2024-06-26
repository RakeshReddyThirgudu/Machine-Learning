# -*- coding: utf-8 -*-
"""Activity 10.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15s1Mli-N6ZtC3EMVFXkhD132WWS-5bEL

# Topic Modeling 

In this activity we will use the Bag-of-Words (BOW) approach for text feature constructions, and LDA for topic modeling. 
We will use the gensim, nltk, and pyLDSvis libraries.
"""

#run once!
!pip install gensim==4.0.1
!pip install pyldavis==3.3.1

import gensim
import pyLDAvis

"""## Data & Scenario

We will use a dataset on restaurant reviews for this exercise. We can explore whether there are certain topics that people write about in their reviews. These topics can be used to come pu with different strategies to engage with users on online platforms. 

This is a small dataset for learning purposes and to avoid long processing times.
You can use any other textual data as input. Depending on the data format, you may have to use different functions to import your text data. Once you have your data imported as a dataframe, where one colum contains the *documents*, the rest will be the same.

Download the file "**Restaurant_Reviews.tsv**" form elearn and upload it to your session before processing. 
"""

# importing restaurant reviews dataset
import pandas as pd
df=pd.read_csv('Restaurant_Reviews.tsv',delimiter="\t")
df.head(2)

"""The sentiment for each review has been manually labeled for this dataset, we will use it in another activity on sentimenet analysis. Here, we only use the Review content for the topic modeling. 

There are 1000 reviews. In NLP terminology, each Review is a ***document***.
"""

len(df)
docs=df['Review']
docs=docs.drop_duplicates() #drop duplicate reviews
docs=docs.values
len(docs)

"""##Text Pre-processing

The pre-processing steps include:
* tokenization: extracting the single words in each document
* remove possible tags, e.g., characters from html documents 
* lowercase/uppercase all words (to not double count)
* (optional) remove multiple whitespaces
* remove punctuations 
* (optional) remove words that are shorter than 3 characters 
* remove stopwords; there are several stopword lists you can use, we use the default built-in from the gensim library
* lemmatize words, using the NLTK implementation
* stem words

We will first apply each step on only one document (review) to see what exactly happens and then apply them on all documents. 
"""

#installing and importing libraries we need
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
nltk.download('wordnet')
from gensim.parsing.preprocessing import strip_multiple_whitespaces,strip_numeric,strip_punctuation,strip_tags,strip_short,remove_stopwords,stem_text

#Let take a look at 1 review
docs[3]

tmp=strip_tags(docs[3]) #removing any tags (such as from html input) 
#changing all words to lower case, since we do not want to double count words 
tmp=tmp.lower() 
tmp

tmp=strip_multiple_whitespaces(tmp) #remove consequent whitespaces
tmp=strip_punctuation(tmp) #remove punctuations
tmp

#remove words that are shorter than 3 characters
tmp=strip_short(tmp, minsize=3)
tmp=remove_stopwords(tmp) #remove stopwords: is, the, as, etc.
tmp

tmp=WordNetLemmatizer().lemmatize(tmp) #lemmatize words
tmp

#stem words
tmp=stem_text(tmp)
tmp

#list the tokens 
list(gensim.utils.tokenize(tmp,deacc=True))

# If you want to apply all the above pre-processing steps you can also use the following function in the gensim library
# For selective pre-processing steps (or just to know how exactly you are processing text) use the above approach
gensim.parsing.preprocessing.preprocess_string(docs[3])

"""## Applying pre-processing steps on corpus
Now we will apply these steps except for stemming on our all documents (i.e., collection of all documents) and save it as a 2D list, "text_data1".
"""

text_data1 = []
for eachdoc in docs:
  tmp=strip_tags(eachdoc)
  tmp=tmp.lower()
  tmp=strip_multiple_whitespaces(tmp)
  tmp=strip_punctuation(tmp)
  tmp=strip_short(tmp)
  tmp=remove_stopwords(tmp)
  tmp=WordNetLemmatizer().lemmatize(tmp)
  #tmp=stem_text(tmp)
  text_data1.append(list(gensim.utils.tokenize(tmp,deacc=True)))

# To apply all pre-processing steps you can also use the following function in gensim 
# strip_tags(),strip_punctuation(),strip_multiple_whitespaces(),strip_numeric(),remove_stopwords(),strip_short(),stem_text()
text_data2=gensim.parsing.preprocessing.preprocess_documents(docs)

"""* text_data1, tokenization with pre-processing steps without stemming
* text_data2, tokenization with all pre-processing steps 

both have equal length but the number of words for some documents may differ. 
"""

len(text_data1),len(text_data2)

"""## Build dictionary from tokenized documents
Next, we build our dictionary based on the tokenized documents. Our dictionary is the collection of all unique words in our corpus. 
Sometimes, words that are very rare or very frequent are dropped fro teh dictionary. We do not do it for our small dataset. 

Each unique word is assigned a number in our dictionary.
"""

from gensim import corpora
dictionary = corpora.Dictionary(text_data1) 
#dictionary.filter_extremes(no_below=15, no_above=0.5, keep_n=100000) #optional

"""## Build corpus represenation based on word frequency
Then we build the mathematical represenation (i.e., document-term matrix) of our corpus based on the frequency of words appearing in each document. 

*corpus_bow* contains the frequency of each word (using the words numeric reference based on our dictionary) for each document.
"""

# corpus using word frequencies 
corpus_bow = [dictionary.doc2bow(text) for text in text_data1]
print('Number of unique tokens: %d' % len(dictionary))
print('Number of documents: %d' % len(corpus_bow))

# one of the documents in our corpus and its numerical representation using word frequencies in corpus_bow
print(docs[3])
print(text_data1[3])
print(corpus_bow[3])

"""## Build corpus representation based on TF-IDF

Mere word frequencies are not the best input for our topic modeling (as well as other text analysis). 
Hence, we also create the mathematical represenation (i.e., document-term matrix) for our corpus based on TF-IDF. 
Note that the we need to first create the word frequencies in order to derive the tf-idf. 

TF-IDF indicates the relative importance of a word within a document relative to the corpus (see slides for formula and simple example). 

For more detail on tf-idf see https://en.wikipedia.org/wiki/Tf-idf 
"""

# corpus using TFIDF
tfidf=gensim.models.TfidfModel(corpus_bow)
corpus_tfidf=tfidf[corpus_bow]

# one of the documents in our corpus and its TF-IDF representation in corpus_tfidf

print(text_data1[3])
print(corpus_tfidf[3])

"""### Question 1
Based on the values in corpus_bow and corpus_tfidf for the 3rd document (in the above cells). 
Are all words in the 3rd review equally important in on both document-term matrices? 

ANSWER: No.

In which representation are the words in the 3rd review weighted based on their total frequency in our corpus? 

ANSWER: corpus_bow representation.

## Using LDA for topic modeling

Topic modeling is exploratory in nature and we have to specify the number of topics we want the algorithm to derive. 

Each topic will be a collection of words from our vocabulary. 

It is usual to try several values and evaluating the results. 
We will build topic models with 3, 5, and 10 topics using both corpus_bow (doc-term matrix of term frequencies) and corpus_tfidf (doc-term matric of TF-IDFs).
"""

# topic models using LDA
from gensim.models import LdaModel
# using document-term matrix of TF
lda_bow_model2 = LdaModel(corpus_bow, num_topics = 2, id2word=dictionary, passes=5,eval_every=None)
lda_bow_model3 = LdaModel(corpus_bow, num_topics = 3, id2word=dictionary, passes=5,eval_every=None)
lda_bow_model5 = LdaModel(corpus_bow, num_topics = 5, id2word=dictionary, passes=5,eval_every=None)

# using document-term matrix of TF-IDF
lda_tfidf_model2 = LdaModel(corpus_tfidf, num_topics = 2, id2word=dictionary, passes=5,eval_every=None)
lda_tfidf_model3 = LdaModel(corpus_tfidf, num_topics = 3, id2word=dictionary, passes=5,eval_every=None)
lda_tfidf_model5 = LdaModel(corpus_tfidf, num_topics = 5, id2word=dictionary, passes=5,eval_every=None)

"""## Explore the topic models
Let's take a look at the most probable words for each topic in the model with 3 topics. 

You can check the top words for the other topic models as well. 
"""

# top words for the 3-topic model based on TF
lda_bow_model3.show_topics(num_words=10)

# top words for the 3-topic model based on TF-IDF
lda_tfidf_model3.show_topics(num_words=5)

"""### Question 2
What seems to be the difference between the topic models (with topics = 3) using TF vs TF-IDF as the input? 

ANSWER: The frequency is represented in TF-IDF but not in TF representation.

## Visualizing topic models 
An important part in exploratory analysis in the interpretation of results. 
Visualizing the topics for a topic model can help a lot. 

We use the LDAvis library that provides methods for visualizing and evluating topics models. 

The next two visualizations are for the same models we checked the top words above.
"""

import pyLDAvis.gensim_models

# visualizing topics for the model with 3 topics based on TFs
lda_display1 = pyLDAvis.gensim_models.prepare(lda_bow_model3, corpus_bow, dictionary, sort_topics=False)
pyLDAvis.display(lda_display1)

# visualizing topics for the model with 3 topics based on TF-IDF
lda_display2 = pyLDAvis.gensim_models.prepare(lda_tfidf_model3, corpus_tfidf, dictionary, sort_topics=False)
pyLDAvis.display(lda_display2)

"""### Question 3 
If you were to chose 3 topics, which model would you choose? why?

ANSWER: I choose IDA model based on TF-IDF input because model with TF-IDF is more understandable between the models.

### Question 4
Can you interpret/characterize the 3 topics from the lda model using TF-IDF (lda_tfidf_model3) in terms of most relevant terms in each topic? (explore the above visualization)

ANSWER: The first topic talks about a great period and place.

The second topic are both positive and negative.

The third subject is excellent cuisine and a welcoming atmosphere. The word "won" is used most commonly in the third topic.

## Retrieve a document/review's score for each topic

Each document in our corpus has a weight for each of the topics in a topic model. 
The topic with the highest score is the one the document is assigned to.

The following cell extracts these scores for one of the documents in our corpus (i.e., one of the reviews).
"""

docs[194] # review 35 (note the index starts at 0)

# check which topic this document is assigned to in the lda_tfidf_model3  model 
# and the top words for each topic
for index, score in lda_tfidf_model3[corpus_tfidf[194]]:
    print("\nScore: {}\t \nTopic: {}".format(score, lda_tfidf_model3.print_topic(index, 10)))

"""### Question 5
Based on your interpretation of the 3 topics in question 4, is this review's assignment to the third topic seem reasonable (or surprising)? briefly explain.

ANSWER: The subject assigned to the aforementioned review 35 is appropriate because my understanding of it was consistent with what the model predicted. My understanding of the subject is consistent with review number 35.

###Question 6
Which topic (out of the 3 topics in lda_tfidf_model3) is review 194 assigned to? (update and rerun the last two cells to asnwer this question)

ANSWER: Topic 1  by lda_tfidf_model3.

## What topic would a new review be assigned to?

Let's see which topic(s) a new review would be assigned to.

While topic models are exploratory in nature, their results can be used as input for text classification models. For example if the resulting topics cleraly characterize different themes in our reviews we can use this topics as categories for our reviews in order to better handle customer complains (e.g., a topic characetrized by bad service but good food, another topic characterized by good atmosphere but mediocre food, etc.)
"""

new_review="The food was too salty but I liked the atmosphere. What's with the attitude?! :-/ "

#applying same pre-processing steps to new review
tmp=strip_tags(new_review)
tmp=tmp.lower()
tmp=strip_multiple_whitespaces(tmp)
tmp=strip_punctuation(tmp)
tmp=strip_short(tmp)
tmp=remove_stopwords(tmp)
tmp=WordNetLemmatizer().lemmatize(tmp)
new=(list(gensim.utils.tokenize(tmp,deacc=True)))
new

# creating a word vector from the tokenized review
bow_vector = dictionary.doc2bow(new)
bow_vector

# assigning new document to the topics in the lda_tfidf_model3
for index, score in lda_tfidf_model3[bow_vector]:
    print("Score: {}\t Topic: {}".format(score, lda_tfidf_model3.print_topic(index, 5)))

# assigning new document to the topics in the lda_bow_model3
for index, score in lda_bow_model3[bow_vector]:
    print("Score: {}\t Topic: {}".format(score, lda_bow_model3.print_topic(index, 5)))

"""## Question 7
Which of the two above assignments for the new review is more appropriate? i.e. should we assign it to topics generated by lda_tfidf_model3 or lda_bow_model3? 


Why?

ANSWER: The lda_bow_model3-generated topics can be given the updated review. Because the terms used in the review correspond to the words that appear most frequently in the subject that the lda_bow_model3 assigned.

# Additional resources

For more details on NLTK, see https://www.nltk.org/ 

For more details on gensim, see https://radimrehurek.com/gensim/

## Visualizing Topic difference within/between models
"""

def plot_difference(mdiff, title="", annotation=None):
    """Plot the difference between models.

    Uses plotly as the backend."""
    import plotly.graph_objs as go
    import plotly.offline as py

    annotation_html = None
    if annotation is not None:
        annotation_html = [
            [
                "+++ {}<br>--- {}".format(", ".join(int_tokens), ", ".join(diff_tokens))
                for (int_tokens, diff_tokens) in row
            ]
            for row in annotation
        ]

    data = go.Heatmap(z=mdiff, colorscale='RdBu', text=annotation_html)
    layout = go.Layout(width=950, height=950, title=title, xaxis=dict(title="topic"), yaxis=dict(title="topic"))
    py.iplot(dict(data=[data], layout=layout))

import numpy as np
num_topics=5
mdiff = np.ones((num_topics, num_topics))
np.fill_diagonal(mdiff, 0.)
plot_difference(mdiff, title="Topic difference (one model) in ideal world")

mdiff, annotation = lda_tfidf_model5.diff(lda_tfidf_model5, distance='jaccard', num_words=50)
plot_difference(mdiff, title="Topic difference (one model) [jaccard distance]", annotation=annotation)

mdiff, annotation = lda_tfidf_model5.diff(lda_tfidf_model5, distance='hellinger', num_words=50)
plot_difference(mdiff, title="Topic difference (one model)[hellinger distance]", annotation=annotation)

mdiff, annotation = lda_bow_model5.diff(lda_bow_model5, distance='jaccard', num_words=50)
plot_difference(mdiff, title="Topic difference (two models)[jaccard distance]", annotation=annotation)