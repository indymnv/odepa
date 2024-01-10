import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 

df = pd.read_csv('elaboracion_lactea_chile.csv')
df.head()
df.columns

df.Año.plot()
plt.show()


