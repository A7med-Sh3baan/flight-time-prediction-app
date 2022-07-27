#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask, render_template
import pickle
import joblib
import pandas as pd 
import datetime as dt 

flight_app=Flask(__name__)

@flight_app.route('/', methods = ['GET'])
def homepage():
    Airline1= ['Go Air', 'IndiGo', 'Vistara', 'AirAsia', 'Air India', 'Spicejet', 'flybig', 'TruJet']
    airline2= ['Go Air', 'IndiGo', 'Vistara', 'Air India', 'AirAsia', 'Spicejet', 'TruJet']
    Cabin= ['PE', 'B', 'E']
    Dept_city= ['Mumbai', 'Bengaluru', 'Indore', 'Srinagar', 'Hyderabad', 'Bhubaneswar',
                 'Amritsar', 'Kochi', 'Ranchi', 'Guwahati', 'Chandigarh', 'Patna', 'Nagpur',
                 'Coimbatore', 'Pune', 'Goa', 'New Delhi', 'Chennai', 'Raipur', 'Mangalore',
                 'Kolkata', 'Bagdogra', 'Port Blair', 'Thiruvananthapuram', 'Lucknow', 'Jaipur',
                 'Visakhapatnam', 'Varanasi', 'Kozhikode', 'Tiruchirappalli']
    
    return render_templates('Airlineform.html')

@flight_app.route('/', methods=['POST'])
def predict():
    if request.method == 'POST':
        IATA = {'Amritsar': ['ATQ'],
                    'Bagdogra': ['IXB'],
                    'Bengaluru': ['BLR'],
                    'Bhubaneswar': ['BBI'],
                    'Chandigarh': ['IXC'],
                    'Chennai': ['MAA'],
                    'Coimbatore': ['CJB'],
                    'Goa': ['GOI'],
                    'Guwahati': ['GAU'],
                    'Hyderabad': ['HDD'],
                    'Indore': ['IDR'],
                    'Jaipur': ['JAI'],
                    'Kochi': ['COK'],
                    'Kolkata': ['CCU'],
                    'Kozhikode': ['CCJ'],
                    'Lucknow': ['LKO'],
                    'Mangalore': ['IXE'],
                    'Mumbai': ['BOM'],
                    'Nagpur': ['NAG'],
                    'New Delhi': ['DEL'],
                    'Patna': ['PAT'],
                    'Port Blair': ['IXZ'],
                    'Pune': ['PNQ'],
                    'Raipur': ['RPR'],
                    'Ranchi': ['IXR'],
                    'Srinagar': ['SXR'],
                    'Thiruvananthapuram': ['TRV'],
                    'Tiruchirappalli': ['TRZ'],
                    'Varanasi': ['VNS'],
                    'Visakhapatnam': ['VTZ']}
        

        dcity=request.form['departure_Time']
        acity=request.form['Arrival_city'].lower()
        cabin=request.form['Cabin']
        arrival_city = request.form['arivcity']
        Airline1 = request.form['Airline1']
        Airline2 = request.form['Airline2']
        departure_time = request.form['departureTime']
        arrival_time = request.form['arrivTime']
        Dept_city = request.form['deptcity']
        arrival_city = request.form['arivcity']
        Airline1 = request.form['airline1']
        Airline2 = request.form['airline2']
        if (not Airline2) and (Airline1 == 'flybig'):
            return Home()
        if not Airline2:
            Airline2 = Airline1
        Cabin = request.form['Cabin']
        stops = int(request.form['Stops'])
        city = Dept_city
        date = request.form['Date']
        datetime = dt.datetime.strptime(date, '%Y-%m-%d')
        weekday = datetime.weekday()
        Dept_date = datetime.month
        x = departure_time.split(':')
        departure_time_minutes = int(x[0]) * 60 + int(x[1])
        x = arrival_time.split(':')
        arrival_time_minutes = int(x[0]) * 60 + int(x[1])
        duration = arrival_time_minutes - departure_time_minutes
        if duration < 0:
            duration *= -1
        Code = IATA[Dept_city][0]
        IATA = Code
        x = departure_time.split(':')
        dept_hours = int(x[0])
        with open("pickleFiles/ordinal_encoder.pkl", "rb") as ordinalEncoder:
            ordinalEncoderObject = pkl.load(ordinalEncoder)
        with open("pickleFiles/ordinal_encoder_time.pkl", "rb") as ordinalEncoderTime:
            ordinalEncoderObjectTime = pkl.load(ordinalEncoderTime)
        data = {}
        for feacher in ['Cabin', 'Airline1', 'Airline2', 'Dept_city', 'arrival_city',
                         'city', 'Code', 'duration', 'arrival_time_minutes', 'departure_time_minutes', 'stops',
                         'dept_hours']:
            data[feacher] = eval(feacher)
        data2 = {}
        for feacher in ['Cabin', 'Airline1', 'Airline2', 'Dept_city', 'arrival_city', 'weekday', 'Dept_date',
                         'duration', 'arrival_time_minutes', 'departure_time_minutes', 'stops',
                         'dept_hours']:
            data2[feacher] = eval(feacher)
        data['City Code'] = IATA
        Dept_flights_time = 0
        if dept_hours < 12 and dept_hours >= 0:
            Dept_flights_time = 'Morning_flight'
        elif dept_hours < 17 and dept_hours >= 12:
            Dept_flights_time = 'Afternoon_flight'
        elif dept_hours < 21 and dept_hours >= 17:
            Dept_flights_time = 'Evening_flight'
        else:
            Dept_flights_time = 'Night_flight'
        data['Dept_flights_time'] = Dept_flights_time
        data2['Dept_flights_time'] = Dept_flights_time
        data['Country Code'] = 'IN'

        df = pd.DataFrame(data, index=[0])
        df2 = pd.DataFrame(data2, index=[0])
        df2['Cabin'] = df2['Cabin'].replace({'E': 0, 'B': 1, 'PE': 2})
        columns = ['Cabin', 'Dept_flights_time', 'Country Code', 'Airline1', 'Airline2',
                'Dept_city', 'arrival_city', 'city', 'City Code', 'Code']
        columns2 = ['Dept_flights_time','Airline1','Airline2','Dept_city','arrival_city']
        df[columns] = ordinalEncoderObject.transform(df[columns])
        df2[columns2] = ordinalEncoderObjectTime.transform(df2[columns2])

        df = df.drop(columns=['Country Code', 'Dept_flights_time', ])
        data.pop('Dept_flights_time', None)
        data.pop('Country Code', None)
        pred = 0
        
        if Cabin == 'B':
            with open('Pipeline For CabinB', "rb") as f:
                model_price = joblib.load(f)
            pred = model_price.predict(df)
        elif Cabin == 'PE':
            with open('Pipeline For CabinPE', "rb") as f:
                model_price = joblib.load(f)
            pred = model_price.predict(df)
        elif Cabin == 'E':
            with open('Pipeline For CabinE', "rb") as f:
                model_price = joblib.load(f)
            pred = model_price.predict(df)
        if data['Airline1'] != data['Airline2']:
            data['Airline'] = data['Airline1'] + ', ' + data['Airline2']
        else:
            data['Airline'] = data['Airline1']
        data.pop('Airline1', None)
        data.pop('Airline2', None)
        data['Departure City'] = data['Dept_city']
        data.pop('Dept_city', None)
        data['Arrival City'] = data['arrival_city']
        data.pop('arrival_city', None)
        data['IATA Code'] = data['Code']
        data.pop('Code', None)
        data['duration'] = str(data['duration']) + ' Minutes'
        data['Departure time'] = departure_time
        data.pop('departure_time_minutes', None)
        data['Arrival time'] = arrival_time
        data.pop('arrival_time_minutes', None)
        data.pop('dept_hours', None)
        data.pop('city', None)
        data.pop('City Code', None)
        data['price'] = pred[0]
        Price = data['price']
        df2['Price'] = Price
        data2['Price']= Price
        predTime = 0
        if Cabin == 'E':
            with open('Pipeline For CabinE', "rb") as f:
                model_price = joblib.load(f)
            predTime = model_price.predict(df2)
        elif Cabin == 'PE':
            with open('Pipeline For CabinPE', "rb") as f:
                model_price = joblib.load(f)
            predTime = model_price.predict(df2)
        elif Cabin == 'B':
            with open('Pipeline For CabinB', "rb") as f:
                model_price = joblib.load(f)
            predTime = model_price.predict(df2)
        if data2['Airline1'] != data2['Airline2']:
            data2['Airline'] = data2['Airline1'] + ', ' + data2['Airline2']
        else:
            data2['Airline'] = data2['Airline1']
        data2.pop('Airline1', None)
        data2.pop('Airline2', None)
        data2['Departure City'] = data2['Dept_city']
        data2.pop('Dept_city', None)
        data2['Arrival City'] = data2['arrival_city']
        data2.pop('arrival_city', None)
        data2['Date'] = date
        data2.pop('weekday', None)
        data2.pop('Dept_date', None)
        data2['duration'] = str(data2['duration']) + ' Minutes'
        data2['Departure time'] = departure_time
        data2.pop('departure_time_minutes', None)
        data2['Arrival time'] = arrival_time
        data2.pop('arrival_time_minutes', None)
        data2.pop('dept_hours', None)
        data2.pop('Dept_flights_time', None)
        data2['optimal hour'] = str(int(predTime[0])) + ':00'
        return render_template('Price.html')



        
if __name__ == "__main__":
    flight_app.run(depug = True)


# In[ ]:




