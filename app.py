import streamlit as st
import pandas as pd
import time
from datetime import datetime
import random

# Define emission factors (example values, replace with accurate data)
EMISSION_FACTORS = {
    "India": {
        "Transportation": 0.14,  # kgCO2/km
        "Electricity": 0.82,  # kgCO2/kWh
        "Diet": {
            "Vegetarian": 0.7,    # kgCO2/meal
            "Non-vegetarian": 1.5, # kgCO2/meal
            "Vegan": 0.5          # kgCO2/meal
        },
        "Waste": 0.1  # kgCO2/kg
    },
    "United States": {
        "Transportation": 0.18,  # kgCO2/km
        "Electricity": 0.42,     # kgCO2/kWh
        "Diet": {
            "Vegetarian": 0.8,    # kgCO2/meal
            "Non-vegetarian": 1.8, # kgCO2/meal
            "Vegan": 0.6          # kgCO2/meal
        },
        "Waste": 0.12  # kgCO2/kg
    },
    "European Union": {
        "Transportation": 0.16,  # kgCO2/km
        "Electricity": 0.28,     # kgCO2/kWh
        "Diet": {
            "Vegetarian": 0.75,    # kgCO2/meal
            "Non-vegetarian": 1.6,  # kgCO2/meal
            "Vegan": 0.55          # kgCO2/meal
        },
        "Waste": 0.09  # kgCO2/kg
    }
}

# Global average for comparison
GLOBAL_AVERAGE_EMISSIONS = {
    "India": 1.9,
    "United States": 15.2,
    "European Union": 6.4
}

# Reduction tips for each category
REDUCTION_TIPS = {
    "Transportation": [
        "Consider carpooling or using public transportation",
        "Try biking or walking for short distances",
        "If possible, work from home a few days a week",
        "Consider an electric or hybrid vehicle for your next purchase",
        "Combine errands to reduce trips"
    ],
    "Electricity": [
        "Switch to LED bulbs throughout your home",
        "Unplug electronics when not in use",
        "Use energy-efficient appliances",
        "Install solar panels if feasible",
        "Wash clothes in cold water and air dry when possible"
    ],
    "Diet": [
        "Consider incorporating more plant-based meals",
        "Reduce food waste by planning meals carefully",
        "Buy local and seasonal produce when possible",
        "Limit beef consumption, as it has the highest carbon footprint",
        "Grow some of your own vegetables if you have space"
    ],
    "Waste": [
        "Compost food scraps when possible",
        "Recycle diligently according to local guidelines",
        "Choose products with minimal packaging",
        "Repair items instead of replacing them",
        "Use reusable bags, bottles, and containers"
    ]
}

# AI assistant responses
AI_RESPONSES = {
    "greeting": [
        "Hello! I'm your carbon footprint assistant. How can I help you today?",
        "Welcome to the Carbon Calculator! I'm here to help you understand and reduce your carbon footprint.",
        "Hi there! Ready to calculate your environmental impact? I'm here to assist!"
    ],
    "high_emissions": [
        "I notice your emissions are above average. Would you like some tips to reduce your carbon footprint?",
        "Your carbon footprint seems higher than the national average. I can suggest some ways to bring it down if you'd like.",
        "Based on your results, there are several opportunities to reduce your emissions. Would you like some specific recommendations?"
    ],
    "low_emissions": [
        "Great job! Your emissions are below average. Would you like some tips to reduce your footprint even further?",
        "You're doing well compared to the national average! I can still offer some tips to help you be even more eco-friendly.",
        "Your carbon footprint is relatively low - nicely done! Want to know how to make an even bigger positive impact?"
    ],
    "specific_high": {
        "Transportation": "I notice your transportation emissions are significant. Have you considered alternatives like public transit or carpooling?",
        "Electricity": "Your electricity usage accounts for a large portion of your footprint. Would you like tips on energy conservation?",
        "Diet": "Your diet has a substantial impact on your carbon footprint. Would you like to learn about more sustainable food choices?",
        "Waste": "Your waste generation is contributing significantly to your emissions. Would you like some tips on reducing waste?"
    }
}

# Set wide layout and page name
st.set_page_config(layout="wide", page_title="Personal Carbon Calculator", page_icon="🌍")

# Add CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #2c3e50;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #34495e;
    }
    .category-title {
        font-weight: bold;
        font-size: 1.2rem;
    }
    .info-box {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .chat-container {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        height: 400px;
        overflow-y: auto;
        background-color: #f9f9f9;
    }
    .user-message {
        background-color: #dcf8c6;
        padding: 8px 12px;
        border-radius: 15px;
        margin: 5px;
        margin-left: 20%;
        margin-right: 5px;
        display: inline-block;
        max-width: 80%;
        float: right;
        clear: both;
    }
    .bot-message {
        background-color: #ffffff;
        padding: 8px 12px;
        border-radius: 15px;
        margin: 5px;
        margin-right: 20%;
        display: inline-block;
        max-width: 80%;
        float: left;
        clear: both;
    }
    .time-stamp {
        font-size: 0.7rem;
        color: #888;
        margin-top: 2px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'calculated' not in st.session_state:
    st.session_state.calculated = False
if 'total_emissions' not in st.session_state:
    st.session_state.total_emissions = 0
if 'transportation_emissions' not in st.session_state:
    st.session_state.transportation_emissions = 0
if 'electricity_emissions' not in st.session_state:
    st.session_state.electricity_emissions = 0
if 'diet_emissions' not in st.session_state:
    st.session_state.diet_emissions = 0
if 'waste_emissions' not in st.session_state:
    st.session_state.waste_emissions = 0
if 'chart_data' not in st.session_state:
    st.session_state.chart_data = None
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": random.choice(AI_RESPONSES["greeting"]), "time": datetime.now().strftime("%H:%M")}
    ]
if 'highest_category' not in st.session_state:
    st.session_state.highest_category = ""

# Streamlit app code
st.markdown("<h1 class='main-header'>🌍 Personal Carbon Calculator</h1>", unsafe_allow_html=True)

# Create tabs
tab1, tab2 = st.tabs(["Calculator", "Chat Assistant"])

with tab1:
    # User inputs
    st.markdown("<h2 class='sub-header'>Enter Your Information</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<p class='category-title'>🌎 Your Location</p>", unsafe_allow_html=True)
        country = st.selectbox("Select your country", ["India", "United States", "European Union"])
        
        st.markdown("<p class='category-title'>🚗 Daily Transportation</p>", unsafe_allow_html=True)
        transportation_mode = st.selectbox("Primary mode of transportation", ["Car", "Public Transit", "Walking/Cycling", "Mixed"])
        distance = st.slider("Daily commute distance (in km)", 0.0, 100.0, 10.0, key="distance_input")
        
        st.markdown("<p class='category-title'>💡 Electricity Usage</p>", unsafe_allow_html=True)
        electricity = st.slider("Monthly electricity consumption (in kWh)", 0.0, 1000.0, 200.0, key="electricity_input")
        
    with col2:
        st.markdown("<p class='category-title'>🍽️ Dietary Habits</p>", unsafe_allow_html=True)
        diet_type = st.selectbox("Diet type", ["Vegetarian", "Non-vegetarian", "Vegan"])
        meals = st.number_input("Number of meals per day", 0, 6, 3, key="meals_input")
        
        st.markdown("<p class='category-title'>🗑️ Waste Generation</p>", unsafe_allow_html=True)
        waste = st.slider("Waste generated per week (in kg)", 0.0, 100.0, 5.0, key="waste_input")
        
        st.markdown("<p class='category-title'>🏠 Housing</p>", unsafe_allow_html=True)
        household_size = st.number_input("Number of people in household", 1, 10, 3)
    
    # Transportation adjustment based on mode
    transport_multiplier = 1.0
    if transportation_mode == "Public Transit":
        transport_multiplier = 0.6
    elif transportation_mode == "Walking/Cycling":
        transport_multiplier = 0.1
    elif transportation_mode == "Mixed":
        transport_multiplier = 0.8
    
    # Calculate button
    if st.button("Calculate My Carbon Footprint"):
        with st.spinner("Calculating your carbon footprint..."):
            time.sleep(1)  # Adding a slight delay for better UX
            
            # Normalize inputs to yearly values
            yearly_distance = distance * 365 * transport_multiplier  # Convert daily distance to yearly with transport mode adjustment
            yearly_electricity = electricity * 12 / household_size  # Convert monthly electricity to yearly per person
            yearly_meals = meals * 365  # Convert daily meals to yearly
            yearly_waste = waste * 52 / household_size  # Convert weekly waste to yearly per person
            
            # Calculate carbon emissions
            transportation_emissions = EMISSION_FACTORS[country]["Transportation"] * yearly_distance
            electricity_emissions = EMISSION_FACTORS[country]["Electricity"] * yearly_electricity
            diet_emissions = EMISSION_FACTORS[country]["Diet"][diet_type] * yearly_meals
            waste_emissions = EMISSION_FACTORS[country]["Waste"] * yearly_waste
            
            # Convert emissions to tonnes and round off to 2 decimal points
            transportation_emissions = round(transportation_emissions / 1000, 2)
            electricity_emissions = round(electricity_emissions / 1000, 2)
            diet_emissions = round(diet_emissions / 1000, 2)
            waste_emissions = round(waste_emissions / 1000, 2)
            
            # Calculate total emissions
            total_emissions = round(
                transportation_emissions + electricity_emissions + diet_emissions + waste_emissions, 2
            )
            
            # Store results in session state
            st.session_state.calculated = True
            st.session_state.total_emissions = total_emissions
            st.session_state.transportation_emissions = transportation_emissions
            st.session_state.electricity_emissions = electricity_emissions
            st.session_state.diet_emissions = diet_emissions
            st.session_state.waste_emissions = waste_emissions
            
            # Create chart data
            chart_data = pd.DataFrame({
                'Category': ['Transportation', 'Electricity', 'Diet', 'Waste'],
                'Emissions (tonnes CO2/year)': [transportation_emissions, electricity_emissions, diet_emissions, waste_emissions]
            })
            st.session_state.chart_data = chart_data
            
            # Determine highest emission category
            emissions_dict = {
                'Transportation': transportation_emissions,
                'Electricity': electricity_emissions,
                'Diet': diet_emissions,
                'Waste': waste_emissions
            }
            st.session_state.highest_category = max(emissions_dict, key=emissions_dict.get)
            
            # Add AI message about results
            if total_emissions > GLOBAL_AVERAGE_EMISSIONS[country]:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": random.choice(AI_RESPONSES["high_emissions"]),
                    "time": datetime.now().strftime("%H:%M")
                })
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": AI_RESPONSES["specific_high"][st.session_state.highest_category],
                    "time": datetime.now().strftime("%H:%M")
                })
            else:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": random.choice(AI_RESPONSES["low_emissions"]),
                    "time": datetime.now().strftime("%H:%M")
                })
    
    # Display results if calculation has been performed
    if st.session_state.calculated:
        st.markdown("<h2 class='sub-header'>Your Carbon Footprint Results</h2>", unsafe_allow_html=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("Carbon Emissions by Category")
            
            # Bar chart for emissions by category
            st.bar_chart(st.session_state.chart_data.set_index('Category'))
            
            # Category breakdown
            st.info(f"🚗 Transportation: {st.session_state.transportation_emissions} tonnes CO2/year")
            st.info(f"💡 Electricity: {st.session_state.electricity_emissions} tonnes CO2/year")
            st.info(f"🍽️ Diet: {st.session_state.diet_emissions} tonnes CO2/year")
            st.info(f"🗑️ Waste: {st.session_state.waste_emissions} tonnes CO2/year")
            
        with col4:
            st.subheader("Total Carbon Footprint")
            
            # Progress gauge for total emissions
            national_avg = GLOBAL_AVERAGE_EMISSIONS[country]
            max_gauge = max(st.session_state.total_emissions, national_avg * 1.5)
            
            # Total emissions display
            st.success(f"🌍 Your total carbon footprint: {st.session_state.total_emissions} tonnes CO2/year")
            
            # Comparison with national average
            if st.session_state.total_emissions > national_avg:
                st.warning(f"Your emissions are {round((st.session_state.total_emissions/national_avg - 1) * 100, 1)}% higher than the {country} average of {national_avg} tonnes CO2/year")
            else:
                st.success(f"Your emissions are {round((1 - st.session_state.total_emissions/national_avg) * 100, 1)}% lower than the {country} average of {national_avg} tonnes CO2/year")
            
            # Tips for the highest emission category
            st.subheader(f"Tips to Reduce Your {st.session_state.highest_category} Emissions")
            for tip in REDUCTION_TIPS[st.session_state.highest_category][:3]:
                st.markdown(f"✅ {tip}")
            
            # Button to view all tips
            if st.button("Show me more ways to reduce my carbon footprint"):
                st.subheader("Comprehensive Reduction Tips")
                for category, tips in REDUCTION_TIPS.items():
                    with st.expander(f"{category} Tips"):
                        for tip in tips:
                            st.markdown(f"• {tip}")

with tab2:
    st.markdown("<h2 class='sub-header'>Chat with Carbon Footprint Assistant</h2>", unsafe_allow_html=True)
    
    # Display chat messages
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"<div class='user-message'>{message['content']}<div class='time-stamp'>{message['time']}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-message'>{message['content']}<div class='time-stamp'>{message['time']}</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Chat input
    user_input = st.text_input("Ask me about your carbon footprint or how to reduce it:", key="user_input")
    
    # Process user input
    if user_input:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input, "time": datetime.now().strftime("%H:%M")})
        
        # Generate response based on user input
        response = ""
        
        # Simple keyword-based response system
        user_input_lower = user_input.lower()
        
        if "transportation" in user_input_lower or "commute" in user_input_lower or "car" in user_input_lower:
            if st.session_state.calculated:
                response = f"Your transportation emissions are {st.session_state.transportation_emissions} tonnes CO2/year. "
                response += "Here are some tips to reduce them:\n" + "\n".join([f"• {tip}" for tip in REDUCTION_TIPS["Transportation"][:3]])
            else:
                response = "Transportation typically accounts for a significant portion of personal carbon emissions. " 
                response += "To reduce your impact, consider using public transit, carpooling, or cycling when possible."
        
        elif "electricity" in user_input_lower or "energy" in user_input_lower or "power" in user_input_lower:
            if st.session_state.calculated:
                response = f"Your electricity emissions are {st.session_state.electricity_emissions} tonnes CO2/year. "
                response += "Here are some tips to reduce them:\n" + "\n".join([f"• {tip}" for tip in REDUCTION_TIPS["Electricity"][:3]])
            else:
                response = "Electricity usage contributes significantly to your carbon footprint. "
                response += "Using energy-efficient appliances and being mindful of your consumption can help reduce emissions."
        
        elif "diet" in user_input_lower or "food" in user_input_lower or "eat" in user_input_lower:
            if st.session_state.calculated:
                response = f"Your diet-related emissions are {st.session_state.diet_emissions} tonnes CO2/year. "
                response += "Here are some tips to reduce them:\n" + "\n".join([f"• {tip}" for tip in REDUCTION_TIPS["Diet"][:3]])
            else:
                response = "Your dietary choices can have a significant impact on your carbon footprint. "
                response += "Plant-based diets generally have lower carbon emissions than meat-heavy diets."
        
        elif "waste" in user_input_lower or "trash" in user_input_lower or "garbage" in user_input_lower:
            if st.session_state.calculated:
                response = f"Your waste-related emissions are {st.session_state.waste_emissions} tonnes CO2/year. "
                response += "Here are some tips to reduce them:\n" + "\n".join([f"• {tip}" for tip in REDUCTION_TIPS["Waste"][:3]])
            else:
                response = "Waste management plays an important role in your overall carbon footprint. "
                response += "Recycling, composting, and reducing consumption all help minimize waste-related emissions."
        
        elif "total" in user_input_lower or "overall" in user_input_lower or "footprint" in user_input_lower:
            if st.session_state.calculated:
                response = f"Your total carbon footprint is {st.session_state.total_emissions} tonnes CO2/year, "
                national_avg = GLOBAL_AVERAGE_EMISSIONS[country]
                if st.session_state.total_emissions > national_avg:
                    response += f"which is {round((st.session_state.total_emissions/national_avg - 1) * 100, 1)}% higher than the {country} average of {national_avg} tonnes CO2/year."
                else:
                    response += f"which is {round((1 - st.session_state.total_emissions/national_avg) * 100, 1)}% lower than the {country} average of {national_avg} tonnes CO2/year."
            else:
                response = "To see your total carbon footprint, please go to the Calculator tab and enter your information."
        
        elif "tip" in user_input_lower or "help" in user_input_lower or "reduce" in user_input_lower:
            response = "Here are some general tips to reduce your carbon footprint:\n"
            for category, tips in REDUCTION_TIPS.items():
                response += f"\n{category}:\n• {tips[0]}\n• {tips[1]}"
                
        elif "hi" in user_input_lower or "hello" in user_input_lower or "hey" in user_input_lower:
            response = random.choice(AI_RESPONSES["greeting"])
            
        elif "thank" in user_input_lower:
            response = "You're welcome! I'm happy to help you understand and reduce your carbon footprint."
            
        else:
            response = "I'm here to help you understand your carbon footprint and provide tips to reduce it. " 
            response += "You can ask me about specific categories like transportation, electricity, diet, or waste, " 
            response += "or ask for general reduction tips."
        
        # Add assistant response to chat
        st.session_state.messages.append({"role": "assistant", "content": response, "time": datetime.now().strftime("%H:%M")})
        
        # Clear input box after processing
        st.experimental_rerun()

# Footer
st.markdown("""
    <div style="text-align: center; margin-top: 30px; padding: 20px; background-color: #f5f5f5; border-radius: 10px;">
        <h3>About This Calculator</h3>
        <p>This carbon footprint calculator provides an estimate of your personal carbon emissions based on your lifestyle choices. 
        The calculations use average emission factors and may not represent your exact emissions.</p>
        <p>Data sources: National emission factors based on 2021 data.</p>
    </div>
""", unsafe_allow_html=True)
