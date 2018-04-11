import pandas as pd
import random
import time

r = pd.read_csv( 'ratings.csv' )
b = pd.read_csv( 'books.csv' )

assert( len( r.user_id.unique()) == r.user_id.max())
assert( len( r.book_id.unique()) == r.book_id.max())
# # Cleaning up Data

# ## Removing rows that contain duplicate user_id, book_id

print(len(r))
r_duplicates_removed = r.drop_duplicates(['user_id','book_id'])
print(len(r_duplicates_removed))
r=r_duplicates_removed

## Books>=20 only
ruser = r.set_index('user_id',drop=False)
ruser['books_rated']=r['user_id'].value_counts()
ruser.sort_values(by='books_rated').head()
ruser=ruser.drop(ruser[ruser.books_rated<20].index)
print(ruser.sort_values(by='books_rated').head())
r=ruser.reset_index(drop=True)

# ## Extracting only English books 

# In[7]:


b['is_english']=b.language_code=='eng'
b_lang=b[['book_id','is_english']]
rm=r.merge(b_lang,how='inner',on = 'book_id')
rm=rm.drop(rm[rm.is_english==False].index)
rm.head()


# ## Writing Training, Test and Negative files

# In[106]:


bookMax = int(rm.max()['book_id'])
userMax = int(rm.max()['user_id'])
userMax=10
rind = rm.drop(rm[rm.rating<3].index)
#Dropping users giving less than 3 ratings(seen as negative review)
rind = rind.set_index('user_id',drop=False)
rind = rind.drop('is_english',axis=1)
rind = rind.drop('books_rated',axis=1)
univSet = set(range(1,bookMax+1))
testset=pd.DataFrame()
#a.append(rind.loc[10].sample(1))
with open('./gb-10k.test.negative','a') as inp:
    for u in xrange(1,userMax+1):
        x=rind.loc[u].sample(1)
        s='('+str(x.loc[u]['user_id'])+','+str(x.loc[u]['book_id'])+')  '
        neg=random.sample(list(univSet-set(rind.loc[u]['book_id'])),99)
        for it in neg:
            s+=str(it)
            s+='\t'
        s=s.strip('\t')
        s+='\n'
        inp.write(s)
        testset=testset.append(x)
#print neg99
trainset = rind[~rind.isin(testset).all(1)]
# print testset
# trainset.head()
testset.to_csv('./gb-10k.test.rating',sep='\t',index=False,header=False)
trainset.sort_values(by='user_id',inplace=True)
trainset.to_csv('./gb-10k.train.rating',sep='\t',index=False,header=False)
