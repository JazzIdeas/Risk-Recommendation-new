from flask import Flask, render_template, request
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
from openai import OpenAI
#import openai

app = Flask(__name__)

# Set your OpenAI GPT-3 API key here
api_key = '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'
client = OpenAI(api_key = api_key)

# Load data
df = pd.read_csv('3.csv')

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

def get_recommend(input1, input2):
    choice_df1 = df[df['Location']==input2]
    choice_df2 = df[df['Category']==input1]
    selected_indexes = intersection(choice_df1.index, choice_df2.index)
    final_df = df[df.index.isin(selected_indexes)]
    policy_options = final_df['Policy']
    addons_options = final_df['Add-ons']
    return policy_options, addons_options

def list_to_dict_with_counts(input_list):
    item_count = {}
    
    for item in input_list:
        if item in item_count:
            item_count[item] += 1
        else:
            item_count[item] = 1

    return item_count

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        industry = request.form['industry']
        sum_insured = request.form['sum_insured']
        category = request.form['category']
        location = request.form['location']

        print("Got results from")

        # Process the data (you can replace this with your own processing logic)
        result = process_customer_data(name, industry, sum_insured, category, location)

        # Get OpenAI GPT-3 recommendation
        gpt3_recommendation = get_openai_recommendation(result['category'], result['location'], result['addons_options'])

        # Render result page with processed data and OpenAI recommendation
        return render_template('result.html', result=result, gpt3_recommendation=gpt3_recommendation)

    # Render the form page for GET requests
    return render_template('form.html')

def process_customer_data(name, industry, sum_insured, category, location):
    # Replace this with your own processing logic
    result = {
        'name': name,
        'industry': industry,
        'sum_insured': sum_insured,
        'category': category,
        'location': location
    }

    # Get policy and add-ons recommendations
    policies, addons_options = get_recommend(category, location)

    result['policies'] = policies
    result['addons_options'] = addons_options

    # Get counts of policies and add-ons options
    policies_counts = list_to_dict_with_counts(policies)
    addons_counts = list_to_dict_with_counts(addons_options)

    result['policies_counts'] = policies_counts
    result['addons_counts'] = addons_counts

    return result

def get_openai_recommendation(category, location, addons_options):
    
    # Compose prompt
    prompt = f"Given the following details:\nCategory: {category}\nLocation: {location}\nPotential Policy Add-on details:\n{addons_options}\nSuggest the three best potential add-ons from these options. Answer in first person, like you are trying to convince the customer and explain why each recommendation is specifically useful for their personal details and business."

    # Call GPT-3 API
    # response = openai.Completion.create(
    #     engine="text-davinci-002",
    #     prompt=prompt,
    #     max_tokens=150
    # )
    print("Fetching response for open ai")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant to help users find the best insurance options for their specific location, industry needs. Your goal is to convince the customer to purchase new policy and add-ons"},
            {"role": "user", "content": prompt}
        ]
)
    print(response)

    # Extract and return the generated recommendation
    recommendation = response.choices[0].message.content
    return recommendation

if __name__ == '__main__':
    app.run(debug=True)