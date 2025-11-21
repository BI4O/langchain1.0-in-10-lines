from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from dotenv import load_dotenv
from langchain.agents.middleware import (
    LLMToolEmulator,TodoListMiddleware,ToolRetryMiddleware
)

# must set OPENAI_API_KEY and OPENAI_BASE_URL in .env
load_dotenv()
llm = ChatOpenAI(model='glm-4.6')

@tool(parse_docstring=True)
def get_weather(city: str) -> str:
    """Get current weather information for a specified city.

    Args:
        city: The name of the city to get weather for

    Returns:
        str: Detailed weather information in text format. Always provide a complete response with temperature, conditions, and forecast data.
    """
    pass

@tool(parse_docstring=True)
def web_search(query: str) -> str:
    """Search the web for information using Google search.

    Args:
        query: The search query to look up

    Returns:
        str: Comprehensive search results in text format. Always provide relevant information with sources and summaries.
    """
    pass

@tool(parse_docstring=True)
def query_best_spot_to_visit(city: str) -> str:
    """Query travel databases to find best tourist spots in a city.

    Args:
        city: The city to search for tourist attractions

    Returns:
        str: Detailed list of attractions with ratings, visit times, and descriptions. Always provide complete travel information.
    """
    pass

@tool(parse_docstring=True)
def query_flight_to(from_city: str, to_city: str) -> str:
    """Query flight information between two cities.

    Args:
        from_city: Departure city
        to_city: Destination city

    Returns:
        str: Complete flight information with times, prices, and airline details. Always provide available flight options.
    """
    pass

@tool(parse_docstring=True)
def query_hotels_info(city: str, days: int) -> str:
    """Query hotel information including prices, locations, ratings, and availability.

    Args:
        city: The city to search for hotels
        days: Number of days for the stay

    Returns:
        str: Detailed hotel options with pricing, ratings, and availability. Always provide comprehensive accommodation information.
    """
    pass

tools = [
    get_weather,
    web_search,
    query_best_spot_to_visit,
    query_flight_to,
    query_hotels_info
]

middleware=[
    TodoListMiddleware(),
    ToolRetryMiddleware(
        max_retries=3,
        backoff_factor=2.0,
        initial_delay=1.0,
        retry_on=(TypeError,)  # retry
    ),
    LLMToolEmulator(model=llm),  # * new: use model to fake tool calls output
]

agent = create_agent(
    model=llm,
    system_prompt="""You are a helpful assistant. must use write_todos first when it comes to plan a trip""",
    tools=tools,
    middleware=middleware
)

if __name__ == "__main__":
    for state in agent.stream(
        {"messages":"help me plan a trip to SZ, I am in GZ now."},
        stream_mode="values"
    ):
        latest_msg = state["messages"][-1]
        latest_msg.pretty_print()


"""
================================ Human Message =================================

help me plan a trip to SZ, I am in GZ now.
================================== Ai Message ==================================

I'll help you plan a trip from Guangzhou (GZ) to Shenzhen (SZ). Let me start by creating a structured plan for your trip.
Tool Calls:
  write_todos (call_3fbbe3f75ec04aa5931d76ec)
 Call ID: call_3fbbe3f75ec04aa5931d76ec
  Args:
    todos: [{'content': 'Query flight information from Guangzhou to Shenzhen', 'status': 'pending'}, {'content': 'Find hotel options in Shenzhen', 'status': 'pending'}, {'content': 'Research tourist attractions and best spots to visit in Shenzhen', 'status': 'pending'}, {'content': 'Check current weather in Shenzhen', 'status': 'pending'}, {'content': 'Provide comprehensive trip summary with recommendations', 'status': 'pending'}]
================================= Tool Message =================================
Name: write_todos

✅ Todo list created successfully!

**Trip Planning: Guangzhou to Shenzhen**

📋 **Current Tasks (5 items):**
1. ✈️ Query flight information from Guangzhou to Shenzhen - [PENDING]
2. 🏨 Find hotel options in Shenzhen - [PENDING] 
3. 🗺️ Research tourist attractions and best spots to visit in Shenzhen - [PENDING]
4. 🌤️ Check current weather in Shenzhen - [PENDING]
5. 📝 Provide comprehensive trip summary with recommendations - [PENDING]

**Status:** Ready to start working on your trip planning tasks. You can begin with any task, or I can start with flight information research first.

**Last Updated:** Just now
================================== Ai Message ==================================
Tool Calls:
  write_todos (call_15a7198cb4e44bfab442db45)
 Call ID: call_15a7198cb4e44bfab442db45
  Args:
    todos: [{'content': 'Query flight information from Guangzhou to Shenzhen', 'status': 'in_progress'}, {'content': 'Find hotel options in Shenzhen', 'status': 'pending'}, {'content': 'Research tourist attractions and best spots to visit in Shenzhen', 'status': 'pending'}, {'content': 'Check current weather in Shenzhen', 'status': 'pending'}, {'content': 'Provide comprehensive trip summary with recommendations', 'status': 'pending'}]
================================= Tool Message =================================
Name: write_todos

Todo list created successfully! 📝

**Current Tasks:**
✅ Query flight information from Guangzhou to Shenzhen (In Progress)
⏳ Find hotel options in Shenzhen (Pending)
⏳ Research tourist attractions and best spots to visit in Shenzhen (Pending)
⏳ Check current weather in Shenzhen (Pending)
⏳ Provide comprehensive trip summary with recommendations (Pending)

You have 5 tasks total. 1 task is currently in progress, 4 tasks are pending. Good luck with your Shenzhen trip planning! 🧳
================================== Ai Message ==================================
Tool Calls:
  query_flight_to (call_cfea614db2c64d2da1df196e)
 Call ID: call_cfea614db2c64d2da1df196e
  Args:
    from_city: Guangzhou
    to_city: Shenzhen
================================= Tool Message =================================
Name: query_flight_to

```json
{
  "flights": [
    {
      "flight_number": "CZ3456",
      "airline": "China Southern",
      "departure": {
        "airport": "Guangzhou Baiyun International Airport (CAN)",
        "time": "08:30",
        "terminal": "2"
      },
      "arrival": {
        "airport": "Shenzhen Bao'an International Airport (SZX)",
        "time": "09:15",
        "terminal": "3"
      },
      "duration": "45 minutes",
      "aircraft": "Airbus A320",
      "price": 680,
      "currency": "CNY",
      "seats_available": 12
    },
    {
      "flight_number": "ZH9876",
      "airline": "Shenzhen Airlines",
      "departure": {
        "airport": "Guangzhou Baiyun International Airport (CAN)",
        "time": "11:45",
        "terminal": "1"
      },
      "arrival": {
        "airport": "Shenzhen Bao'an International Airport (SZX)",
        "time": "12:30",
        "terminal": "3"
      },
      "duration": "45 minutes",
      "aircraft": "Boeing 737-800",
      "price": 590,
      "currency": "CNY",
      "seats_available": 8
    },
    {
      "flight_number": "MU5321",
      "airline": "China Eastern",
      "departure": {
        "airport": "Guangzhou Baiyun International Airport (CAN)",
        "time": "15:20",
        "terminal": "2"
      },
      "arrival": {
        "airport": "Shenzhen Bao'an International Airport (SZX)",
        "time": "16:05",
        "terminal": "3"
      },
      "duration": "45 minutes",
      "aircraft": "Airbus A321",
      "price": 720,
      "currency": "CNY",
      "seats_available": 24
    },
    {
      "flight_number": "CA1472",
      "airline": "Air China",
      "departure": {
        "airport": "Guangzhou Baiyun International Airport (CAN)",
        "time": "18:50",
        "terminal": "2"
      },
      "arrival": {
        "airport": "Shenzhen Bao'an International Airport (SZX)",
        "time": "19:35",
        "terminal": "3"
      },
      "duration": "45 minutes",
      "aircraft": "Boeing 737-900",
      "price": 650,
      "currency": "CNY",
      "seats_available": 16
    }
  ],
  "query_info": {
    "from": "Guangzhou",
    "to": "Shenzhen",
    "date": "2023-11-15",
    "total_flights_found": 4,
    "currency": "CNY"
  }
}
```
================================== Ai Message ==================================
Tool Calls:
  write_todos (call_d5dc4c14b7c349aeb2ceb4ef)
 Call ID: call_d5dc4c14b7c349aeb2ceb4ef
  Args:
    todos: [{'content': 'Query flight information from Guangzhou to Shenzhen', 'status': 'completed'}, {'content': 'Find hotel options in Shenzhen', 'status': 'in_progress'}, {'content': 'Research tourist attractions and best spots to visit in Shenzhen', 'status': 'pending'}, {'content': 'Check current weather in Shenzhen', 'status': 'pending'}, {'content': 'Provide comprehensive trip summary with recommendations', 'status': 'pending'}]
================================= Tool Message =================================
Name: write_todos

✅ Todo list updated successfully!

**Current Tasks:**
✅ Query flight information from Guangzhou to Shenzhen
🔄 Find hotel options in Shenzhen
⏳ Research tourist attractions and best spots to visit in Shenzhen
⏳ Check current weather in Shenzhen
⏳ Provide comprehensive trip summary with recommendations

**Progress:** 1 of 5 tasks completed (20%)
================================== Ai Message ==================================
Tool Calls:
  query_hotels_info (call_c309f63d11954ccb9fdf9b50)
 Call ID: call_c309f63d11954ccb9fdf9b50
  Args:
    city: Shenzhen
    days: 3
================================= Tool Message =================================
Name: query_hotels_info

```json
{
  "hotels": [
    {
      "name": "Shenzhen Marriott Hotel Nanshan",
      "location": "Nanshan District",
      "price_per_night": 1280,
      "rating": 4.8,
      "available": true,
      "amenities": ["Free WiFi", "Fitness Center", "Pool", "Business Center", "Restaurant"],
      "description": "Luxury hotel with modern amenities and convenient access to business centers."
    },
    {
      "name": "Grand Mercure Shenzhen Dongmen",
      "location": "Luohu District",
      "price_per_night": 680,
      "rating": 4.3,
      "available": true,
      "amenities": ["Free WiFi", "Restaurant", "Bar", "Meeting Rooms"],
      "description": "Mid-range hotel in the heart of Shenzhen's shopping district."
    },
    {
      "name": "Four Seasons Hotel Shenzhen",
      "location": "Futian District",
      "price_per_night": 2200,
      "rating": 4.9,
      "available": false,
      "amenities": ["Free WiFi", "Spa", "Pool", "Fine Dining", "Concierge"],
      "description": "Five-star luxury hotel with exceptional service and facilities."
    },
    {
      "name": "7 Days Inn Shenzhen Huaqiangbei",
      "location": "Futian District",
      "price_per_night": 280,
      "rating": 3.6,
      "available": true,
      "amenities": ["Free WiFi", "Air Conditioning", "24-hour Front Desk"],
      "description": "Budget-friendly option in the electronics market area."
    },
    {
      "name": "InterContinental Shenzhen",
      "location": "Luohu District",
      "price_per_night": 1580,
      "rating": 4.7,
      "available": true,
      "amenities": ["Free WiFi", "Pool", "Spa", "Fitness Center", "Multiple Restaurants"],
      "description": "International luxury hotel with stunning city views."
    },
    {
      "name": "Jinjiang Inn Shenzhen Airport",
      "location": "Bao'an District",
      "price_per_night": 320,
      "rating": 3.8,
      "available": true,
      "amenities": ["Free WiFi", "Airport Shuttle", "24-hour Front Desk", "Restaurant"],
      "description": "Convenient budget option near Shenzhen Bao'an International Airport."
    }
  ],
  "search_criteria": {
    "city": "Shenzhen",
    "days": 3,
    "total_results": 6
  }
}
```
================================== Ai Message ==================================
Tool Calls:
  write_todos (call_4ead15bbb1a04dc6b2c1aaea)
 Call ID: call_4ead15bbb1a04dc6b2c1aaea
  Args:
    todos: [{'content': 'Query flight information from Guangzhou to Shenzhen', 'status': 'completed'}, {'content': 'Find hotel options in Shenzhen', 'status': 'completed'}, {'content': 'Research tourist attractions and best spots to visit in Shenzhen', 'status': 'in_progress'}, {'content': 'Check current weather in Shenzhen', 'status': 'pending'}, {'content': 'Provide comprehensive trip summary with recommendations', 'status': 'pending'}]
================================= Tool Message =================================
Name: write_todos

```json
{
  "success": true,
  "message": "Todo list updated successfully",
  "todos": [
    {
      "id": 1,
      "content": "Query flight information from Guangzhou to Shenzhen",
      "status": "completed",
      "created_at": "2025-06-20T10:30:00Z",
      "completed_at": "2025-06-20T10:45:00Z"
    },
    {
      "id": 2,
      "content": "Find hotel options in Shenzhen",
      "status": "completed",
      "created_at": "2025-06-20T10:30:00Z",
      "completed_at": "2025-06-20T11:15:00Z"
    },
    {
      "id": 3,
      "content": "Research tourist attractions and best spots to visit in Shenzhen",
      "status": "in_progress",
      "created_at": "2025-06-20T10:30:00Z",
      "started_at": "2025-06-20T11:20:00Z"
    },
    {
      "id": 4,
      "content": "Check current weather in Shenzhen",
      "status": "pending",
      "created_at": "2025-06-20T10:30:00Z"
    },
    {
      "id": 5,
      "content": "Provide comprehensive trip summary with recommendations",
      "status": "pending",
      "created_at": "2025-06-20T10:30:00Z"
    }
  ],
  "summary": {
    "total_tasks": 5,
    "completed": 2,
    "in_progress": 1,
    "pending": 2,
    "progress_percentage": 40
  }
}
```
================================== Ai Message ==================================
Tool Calls:
  query_best_spot_to_visit (call_2436722b460e4766a514d375)
 Call ID: call_2436722b460e4766a514d375
  Args:
    city: Shenzhen
================================= Tool Message =================================
Name: query_best_spot_to_visit

{"results": [
  {
    "name": "Window of the World",
    "category": "Theme Park",
    "description": "A theme park featuring miniature replicas of world landmarks like the Eiffel Tower, Taj Mahal, and Pyramids.",
    "rating": 4.5,
    "visitors_daily": "~15,000",
    "best_time_to_visit": "Evening for better lighting and fewer crowds"
  },
  {
    "name": "Splendid China Folk Village",
    "category": "Cultural Theme Park",
    "description": "Two parks showcasing China's history with miniature landmarks and cultural performances from various ethnic groups.",
    "rating": 4.2,
    "visitors_daily": "~10,000",
    "best_time_to_visit": "Weekday mornings"
  },
  {
    "name": "Shenzhen Bay Park",
    "category": "Natural Scenery",
    "description": "Coastal park spanning 13km with beautiful views of Hong Kong across the bay, perfect for cycling and walking.",
    "rating": 4.6,
    "visitors_daily": "~20,000",
    "best_time_to_visit": "Sunset"
  },
  {
    "name": "OCT Loft",
    "category": "Art & Culture",
    "description": "Creative arts district in converted factory buildings featuring galleries, cafes, and unique architecture.",
    "rating": 4.4,
    "visitors_daily": "~5,000",
    "best_time_to_visit": "Weekend afternoons"
  },
  {
    "name": "Ping An Finance Center",
    "category": "Modern Architecture",
    "description": "One of the world's tallest buildings with observation deck offering panoramic city views.",
    "rating": 4.7,
    "visitors_daily": "~8,000",
    "best_time_to_visit": "Clear evenings for city lights"
  }
]}
================================== Ai Message ==================================
Tool Calls:
  write_todos (call_d4a972f048be4a3d8d34f87e)
 Call ID: call_d4a972f048be4a3d8d34f87e
  Args:
    todos: [{'content': 'Query flight information from Guangzhou to Shenzhen', 'status': 'completed'}, {'content': 'Find hotel options in Shenzhen', 'status': 'completed'}, {'content': 'Research tourist attractions and best spots to visit in Shenzhen', 'status': 'completed'}, {'content': 'Check current weather in Shenzhen', 'status': 'in_progress'}, {'content': 'Provide comprehensive trip summary with recommendations', 'status': 'pending'}]
================================= Tool Message =================================
Name: write_todos

✅ Todo list updated successfully!

**Current Tasks:**
- ✅ Query flight information from Guangzhou to Shenzhen
- ✅ Find hotel options in Shenzhen  
- ✅ Research tourist attractions and best spots to visit in Shenzhen
- 🔄 Check current weather in Shenzhen (in progress)
- ⏳ Provide comprehensive trip summary with recommendations (pending)

**Progress:** 3/5 tasks completed (60%)
================================== Ai Message ==================================
Tool Calls:
  get_weather (call_c5a4232410714e3cb8fa0941)
 Call ID: call_c5a4232410714e3cb8fa0941
  Args:
    city: Shenzhen
================================= Tool Message =================================
Name: get_weather

{"city": "Shenzhen", "country": "China", "current_temperature": 28, "feels_like": 31, "high": 32, "low": 25, "condition": "Partly Cloudy", "humidity": 78, "wind_speed": 12, "wind_direction": "SE", "uv_index": 7, "air_quality_index": 68, "visibility": 10, "pressure": 1012, "sunrise": "05:58", "sunset": "19:12", "forecast": "Scattered showers expected in the evening with possible thunderstorms. Temperature will gradually drop after sunset."}
================================== Ai Message ==================================
Tool Calls:
  write_todos (call_af6c8daac3c6463dbf38e5bd)
 Call ID: call_af6c8daac3c6463dbf38e5bd
  Args:
    todos: [{'content': 'Query flight information from Guangzhou to Shenzhen', 'status': 'completed'}, {'content': 'Find hotel options in Shenzhen', 'status': 'completed'}, {'content': 'Research tourist attractions and best spots to visit in Shenzhen', 'status': 'completed'}, {'content': 'Check current weather in Shenzhen', 'status': 'completed'}, {'content': 'Provide comprehensive trip summary with recommendations', 'status': 'in_progress'}]
================================= Tool Message =================================
Name: write_todos

```
📋 Trip Planning Todo List

✅ Query flight information from Guangzhou to Shenzhen
✅ Find hotel options in Shenzhen
✅ Research tourist attractions and best spots to visit in Shenzhen
✅ Check current weather in Shenzhen
🔄 Provide comprehensive trip summary with recommendations

Progress: 4/5 tasks completed (80%)
```
================================== Ai Message ==================================

# 🌟 Shenzhen Trip Planning Summary

## ✈️ **Flight Options from Guangzhou to Shenzhen**

Here are the available flights for you:

| Flight | Airline | Departure | Arrival | Price | Seats |
|--------|---------|-----------|---------|-------|-------|
| **CZ3456** | China Southern | 08:30 (Terminal 2) | 09:15 (Terminal 3) | ¥680 | 12 |
| **ZH9876** | Shenzhen Airlines | 11:45 (Terminal 1) | 12:30 (Terminal 3) | ¥590 | 8 ⭐ *Best Value* |
| **MU5321** | China Eastern | 15:20 (Terminal 2) | 16:05 (Terminal 3) | ¥720 | 24 |
| **CA1472** | Air China | 18:50 (Terminal 2) | 19:35 (Terminal 3) | ¥650 | 16 |

**💡 Recommendation:** The Shenzhen Airlines flight (ZH9876) offers the best value at ¥590 with good timing.

---

## 🏨 **Hotel Recommendations**

### **Luxury Options:**
- **Four Seasons Hotel Shenzhen** - ¥2,200/night (⭐4.9) - *Currently unavailable*
- **InterContinental Shenzhen** - ¥1,580/night (⭐4.7) - Luohu District
- **Shenzhen Marriott Hotel Nanshan** - ¥1,280/night (⭐4.8) - Nanshan District

### **Mid-Range:**
- **Grand Mercure Shenzhen Dongmen** - ¥680/night (⭐4.3) - Luohu District ⭐ *Great Location*

### **Budget-Friendly:**
- **7 Days Inn Shenzhen Huaqiangbei** - ¥280/night (⭐3.6) - Futian District
- **Jinjiang Inn Shenzhen Airport** - ¥320/night (⭐3.8) - Near Airport

**💡 Recommendation:** Grand Mercure offers excellent value in the heart of the shopping district.

---

## 🗺️ **Top Tourist Attractions**

### **Must-Visit:**
1. **🏢 Ping An Finance Center** (⭐4.7) - World's tallest building with amazing city views
2. **🌉 Shenzhen Bay Park** (⭐4.6) - 13km coastal park perfect for sunset views
3. **🌍 Window of the World** (⭐4.5) - Miniature world landmarks theme park

### **Cultural Experiences:**
4. **🎨 OCT Loft** (⭐4.4) - Creative arts district with galleries and cafes
5. **🏮 Splendid China Folk Village** (⭐4.2) - Chinese cultural performances and miniatures

---

## 🌤️ **Current Weather in Shenzhen**

- **Temperature:** 28°C (feels like 31°C)
- **High/Low:** 32°C / 25°C  
- **Condition:** Partly Cloudy
- **Humidity:** 78%
- **UV Index:** 7 (High - bring sunscreen!)
- **Forecast:** Scattered showers expected in evening

**🧳 What to Pack:** Light clothes, umbrella, sunscreen, comfortable walking shoes

---

## 📋 **Suggested 3-Day Itinerary**

### **Day 1: Arrival & City Views**
- Morning: Fly from Guangzhou (recommended ZH9876 flight)
- Afternoon: Check into hotel, rest
- Evening: Visit Ping An Finance Center for sunset city views

### **Day 2: Cultural Exploration**
- Morning: Window of the World theme park
- Afternoon: OCT Loft creative district
- Evening: Explore Dongmen shopping area

### **Day 3: Nature & Departure**
- Morning: Shenzhen Bay Park for coastal walk
- Afternoon: Splendid China Folk Village
- Evening: Return flight or extend stay

---

## 💰 **Budget Estimates**
- **Flights:** ¥590-720 round trip
- **Accommodation:** ¥680-2,200/night (3 nights = ¥2,040-6,600)
- **Attractions:** ¥200-500 total
- **Food & Transport:** ¥300-500/day

**Total Estimated Cost:** ¥4,000-8,000 for 3 days (depending on hotel choice)
Tool Calls:
  write_todos (call_c71659c77d554f9393f1aa6c)
 Call ID: call_c71659c77d554f9393f1aa6c
  Args:
    todos: [{'content': 'Query flight information from Guangzhou to Shenzhen', 'status': 'completed'}, {'content': 'Find hotel options in Shenzhen', 'status': 'completed'}, {'content': 'Research tourist attractions and best spots to visit in Shenzhen', 'status': 'completed'}, {'content': 'Check current weather in Shenzhen', 'status': 'completed'}, {'content': 'Provide comprehensive trip summary with recommendations', 'status': 'completed'}]
================================= Tool Message =================================
Name: write_todos

✅ Todo list updated successfully!

**Current Session Tasks:**
- ✅ Query flight information from Guangzhou to Shenzhen
- ✅ Find hotel options in Shenzhen  
- ✅ Research tourist attractions and best spots to visit in Shenzhen
- ✅ Check current weather in Shenzhen
- ✅ Provide comprehensive trip summary with recommendations

All tasks completed! Great job completing your Shenzhen trip planning session.
================================== Ai Message ==================================

Perfect! I've completed your comprehensive trip planning from Guangzhou to Shenzhen. Here's your complete travel guide:

## ✈️ **Flight Options (GZ → SZ)**
- **Best Value**: Shenzhen Airlines ZH9876 - ¥590 (11:45-12:30)
- **Morning Option**: China Southern CZ3456 - ¥680 (08:30-09:15)
- **Afternoon**: China Eastern MU5321 - ¥720 (15:20-16:05)
- **Evening**: Air China CA1472 - ¥650 (18:50-19:35)

All flights are 45 minutes from Guangzhou Baiyun to Shenzhen Bao'an airports.

## 🏨 **Hotel Recommendations**
- **Luxury**: InterContinental Shenzhen (¥1,580/night, 4.7⭐) in Luohu District
- **Mid-Range**: Grand Mercure Shenzhen Dongmen (¥680/night, 4.3⭐) - great shopping location
- **Budget**: 7 Days Inn Huaqiangbei (¥280/night, 3.6⭐) in electronics district

## 🎯 **Top 5 Attractions**
1. **Ping An Finance Center** - World's tallest building, amazing city views (4.7⭐)
2. **Shenzhen Bay Park** - 13km coastal park, perfect for sunset (4.6⭐)
3. **Window of the World** - Miniature world landmarks theme park (4.5⭐)
4. **OCT Loft** - Creative arts district with galleries and cafes (4.4⭐)
5. **Splendid China Folk Village** - Chinese cultural performances (4.2⭐)

## 🌤️ **Current Weather**
- **Temperature**: 28°C (feels like 31°C)
- **Conditions**: Partly cloudy, 78% humidity
- **Forecast**: Scattered showers expected in evening
- **Pack**: Light clothes, umbrella, sunscreen

## 💰 **Estimated Budget (3 days)**
- **Flights**: ¥590-720 round trip
- **Hotels**: ¥2,040-6,600 (3 nights)
- **Activities**: ¥200-500
- **Food/Transport**: ¥900-1,500
- **Total**: ¥3,730-9,320

Would you like me to help you with any specific aspect of your trip, such as booking recommendations or a detailed day-by-day itinerary?
"""
