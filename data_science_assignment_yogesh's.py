# -*- coding: utf-8 -*-
"""Data_Science_Assignment_Yogesh's.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1bcg-xJMIwE426850Aol6t4iTRL2SooGT

# **Install Dependencies**
"""

import pandas as pd
import numpy as np
!pip install scikit-surprise
from surprise import SVD
from surprise import Dataset, Reader
from surprise.model_selection import train_test_split
from surprise import accuracy

"""## Upload Datasets"""

meta_df = pd.read_csv('/content/metadata.csv')
meta_df.head()

user_df = pd.read_csv('/content/user_interaction.csv')
user_df.head()

user_df.head()

meta_df.head()

"""## Check information ℹ"""

user_df.info()
meta_df.info()

"""## Checking Null values"""

user_df.isnull().sum()

meta_df.isnull().sum()

"""## Duplicates"""

user_df.duplicated().sum()

meta_df.duplicated().sum()

"""## Change Time Date Format"""

user_df["updated_at"] = pd.to_datetime(user_df["updated_at"])

meta_df["updated_at"]= pd.to_datetime(meta_df["updated_at"])

meta_df["published_at"]= pd.to_datetime(meta_df["published_at"])

"""## Checking Data Types"""

user_df.dtypes

meta_df.dtypes

"""## Exploratory Data Analysis"""

import matplotlib.pyplot as plt
import seaborn as sns

user_read_counts = user_df.groupby("user_id")["pratilipi_id"].nunique()

"""## PLOTS"""

plt.figure(figsize=(10,5))
sns.histplot(user_read_counts, bins=50, kde=True)
plt.xlabel("Number of Stories Read per user")
plt.ylabel("Number of users")
plt.title("Distribution of stories Read per user")
plt.show()

user_avg_read= user_df.groupby("user_id")["read_percent"].mean()
user_avg_read

plt.figure(figsize=(10,5))
sns.histplot(user_avg_read,bins=50,kde=True)
plt.xlabel("Average Read Percentage")
plt.ylabel("Number of Users")
plt.title("User Average Read Percentage Distribution")
plt.show()

"""# Tops Stories"""

top_Stories = user_df["pratilipi_id"].value_counts().head(10)
top_Stories

plt.figure(figsize=(12,6))
sns.barplot(x=top_Stories.index, y=top_Stories.values)
plt.xlabel("Pratilipi ID")
plt.ylabel("Top 10 Most Read Stories")
plt.xticks(rotation=45)
plt.show()

"""# Top Categories"""

top_categories = meta_df["category_name"].value_counts().head(10)
top_categories

plt.figure(figsize=(12,6))
sns.barplot(x=top_categories.index,y=top_categories.values)
plt.xlabel("Category")
plt.ylabel("Number of Stories")
plt.title("Top 20 Most Popular Categories")
plt.xticks(rotation=45)
plt.show()

"""## Merging Data"""

merged_data = user_df.merge(meta_df, on="pratilipi_id", how="left")
merged_data.head()

merged_data = merged_data.sort_values(by="updated_at_y")
split_idx = int(len(merged_data)*0.75)
train_data = merged_data.iloc[:split_idx]
test_data = merged_data.iloc[split_idx:]

train_data.shape

test_data.shape

"""## **Recommendations svd_model**"""

!pip install scikit-surprise
from surprise import SVD
from surprise import Dataset, Reader
from surprise.model_selection import train_test_split
from surprise import accuracy

reader = Reader(rating_scale=(0,100))

data = Dataset.load_from_df(train_data[['user_id','pratilipi_id','read_percent']],reader)

"""## **Model Evaluation**"""

trainset, valset = train_test_split(data, test_size=0.25)

svd_model = SVD(n_factors=50, random_state=42)
svd_model.fit(trainset)

"""# **RMSE**"""

predictions = svd_model.test(valset)
rmse = accuracy.rmse(predictions)

"""## **Personalized Story Recommendations**"""

def get_recommendations(user_id,model,all_story_ids,n_recs=5):
    user_read_stories = train_data[train_data['user_id']==user_id]['pratilipi_id'].unique()
    unseen_stories = [story for story in all_story_ids if story not in user_read_stories]
    predictions = [model.predict(user_id, story) for story in unseen_stories]
    predictions.sort(key=lambda x: x.est, reverse=True )
    top_recs = [pred.iid for pred in predictions[:n_recs]]
    return top_recs
all_story_ids = train_data['pratilipi_id'].unique()
recommended_stories = get_recommendations(1,svd_model,all_story_ids)

print(f"Recommended Stories for User 1: {recommended_stories}")

"""## **Model Selection**"""

from surprise.model_selection import RandomizedSearchCV
from surprise import SVD, Dataset, Reader

param_grid = {
    'n_factors': [50, 100],
    'reg_all': [0.02, 0.1],
    'lr_all': [0.005]
}

random_search = RandomizedSearchCV(SVD, param_grid, n_iter=4, measures=['rmse'], cv=2, random_state=42, n_jobs=-1)
random_search.fit(data)

best_params = random_search.best_params['rmse']
print(f"Best Parameters: {best_params}")

best_svd = SVD(**best_params)
trainset = data.build_full_trainset()
best_svd.fit(trainset)

"""## **Unseen Stories Based on User Preferences**"""

def get_recommendations(user_id, model, all_story_ids, n_recs=5):
    user_read_stories = train_data[train_data['user_id']==user_id]['pratilipi_id'].unique()
    unseen_stories = [story for story in all_story_ids if story not in user_read_stories]
    predictions = [model.predict(user_id, story) for story in unseen_stories ]
    predictions.sort(key=lambda x: x.est, reverse=True)

    top_recs = [pred.iid for pred in predictions[:n_recs]]
    return top_recs

all_story_ids = train_data['pratilipi_id'].unique()
user_id = 1
recommended_stories = get_recommendations(user_id, best_svd, all_story_ids)
print(f"Top 5 Recommended Stories for User {user_id}: {recommended_stories}")

"""## **Creating a file containing top 5 stories for each user**"""

import pandas as pd

active_users = train_data['user_id'].value_counts()
active_users = active_users[active_users >= 5].index

top_stories = train_data['pratilipi_id'].value_counts().head(1000).index

recommendations = []
for user in active_users[:5000]:
    top_stories_for_user = get_recommendations(user, best_svd, top_stories, n_recs=5)
    recommendations.append([user] + top_stories_for_user)

recommendations_df = pd.DataFrame(recommendations, columns=['user_id', 'rec_1', 'rec_2', 'rec_3', 'rec_4', 'rec_5'])
recommendations_df.to_csv("recommendations.csv", index=False)

print("Optimized recommendations.csv")