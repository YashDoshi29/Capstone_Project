import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('dark_background')

def plot_spending_distribution(df):
    category_amounts = df.groupby('Category')['Amount'].sum()

    plt.figure(figsize=(8, 8))

    def autopct_func(pct, allvalues):
        absolute = round(pct / 100. * sum(allvalues), 2)
        return f'{pct:.2f}%\n${absolute:.2f}'

    plt.pie(category_amounts, labels=category_amounts.index, autopct=lambda pct: autopct_func(pct, category_amounts),
            startangle=120, colors=plt.cm.Paired.colors, textprops={'color': 'white'}) 

    plt.title('Spending Distribution by Category', color='white', fontsize=16, pad=20)  
    plt.axis('equal') 
    plt.show()
