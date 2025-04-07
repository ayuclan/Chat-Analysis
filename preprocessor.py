import re
import pandas as pd

def preprocess(data):
    # Define patterns for both formats
    pattern1 = r'\[\d{2}/\d{2}/\d{2},\s\d{1,2}:\d{2}:\d{2}\s[APM]{2}\]\s'
    pattern2 = r'\d{2}/\d{2}/\d{4},\s\d{1,2}:\d{2}\s-\s'

    # Check which pattern matches the data
    if re.search(pattern1, data):
        messages = re.split(pattern1, data)[1:]  # Split messages for format 1
        dates = re.findall(pattern1, data)  # Extract dates for format 1
        dates = [date.strip('[] ') for date in dates]
        date_format = '%d/%m/%y, %I:%M:%S %p'
    elif re.search(pattern2, data):
        messages = re.split(pattern2, data)[1:]  # Split messages for format 2
        dates = re.findall(pattern2, data)  # Extract dates for format 2
        dates = [date.strip(' - ') for date in dates]
        date_format = '%d/%m/%Y, %H:%M'

    # Create DataFrame
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    
    # Convert message_date type
    df['message_date'] = pd.to_datetime(df['message_date'], format=date_format)

    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []
    for message in df['user_message']:
        # Handle both formats for user extraction
        if ':' in message:
            entry = re.split('([\w\W]+?):\s', message)
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(message)

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Extract date components
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Create period column
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df
