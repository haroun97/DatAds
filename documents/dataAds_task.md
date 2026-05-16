# DatAds Take-Home Exercise

## Overview

At [DatAds](https://datads.io/), we help marketing teams understand which ad creatives perform best across different platforms. This exercise simulates a core challenge: aggregating data from multiple ad platforms (like Facebook, Google Ads, TikTok) and providing unified insights through an API. In this exercise we are evaluating your capability of building those systems at scale.

**Time Estimate:** 2-6 hours

**Due:** Please submit **latest** 24 hours before interview to give interviewer enough time to review the solution

<aside>
⚠️

**Important Note on Time Management**

We respect your time and understand you have other commitments. Please don't spend more than the estimated time on these tasks. If you find yourself running short on time, we'd much rather see your thought process and approach than a rushed implementation. Feel free to describe what you *would* implement in your documentation rather than coding everything from scratch.

**Remember: This assignment is just the starting point for our technical discussion.** During the follow-up interview, we'll dive deep into your solution, discuss your architectural decisions, and explore how you'd extend or modify your approach. We're much more interested in your reasoning and problem-solving process than having every feature perfectly implemented.

We're primarily interested in:

- Your problem-solving approach and architectural thinking
- How you handle real-world challenges like API integration and error handling
- Your ability to write clean, maintainable code within time constraints
- Your thought process and ability to articulate technical decisions (which we'll discuss in detail during the interview)

Remember, this is about demonstrating your skills and thought process, not about delivering a production-ready system. If you have any questions or need clarification on any requirements, please don't hesitate to reach out to [daniel@datads.io](mailto:daniel@datads.io) - we're here to help!

</aside>

## Part 1 — System Design *(Required)*

### Task

Over the next parts you are building a system that collects ad performance data from multiple advertising platforms, processes it, and provides insights through an API. On a high level your system needs to support the following:

1. Loading raw data from an external API
2. Computing the CTR, CPC and ROAS from the raw data
3. Exposing an API to query the performance metrics

Start by reading and understanding the core functionality the system needs to support. Then sketch the system on a high level. Focus your design on reliability and scalability. How to extract the data at scale? How can we support thousands of requests per second? How to handle failures?

For your design you can use a tool like Lucid or Miro, or you can draw by hand and attach an image of your design to the final submission. Include a brief written explanation (1-2 paragraphs) of your architectural choices.

### Core Functionality

1. **Data Polling**
    - Poll the `Mock API Service` APIs on scheduled intervals
    - Handle different API response formats and pagination
    - Implement rate limiting, retry logic, and error handling
2. **Job Scheduling**
    - Schedule periodic API polling (different frequencies per platform)
    - Handle failed jobs with exponential backoff
3. **Data Processing**
    - Store the ingested data persistently
    - Calculate the following performance metrics from the raw data:
        - `ctr = clicks / impressions`
        - `cpc = spend / clicks`
        - `roas = revenue / spend`
    - Handle duplicate detection and data deduplication
4. **Query API Layer**
    - REST API to query aggregated ad performance data
    - `GET /api/performance`
        - Return the aggregated performance of all available metrics
        - Filter by platform, date range, and campaign
    - `GET /api/top-performing`
        - Return top-performing ads based on different metrics

### Deliverables

- System architecture diagram (image file: .png, .jpg, or .pdf)
- Brief written explanation of your architectural choices (can be in README.md)

## Part 2 — Implement Data Polling and Data Processing *(As far as you come)*

<aside>
⚠️

**Note:** Please don't stress if you can't complete the full part within the time limit. Focus on implementing what you can and document your remaining ideas and approach in your README files. We'll explore these concepts together and discuss your planned solutions during our follow-up interview.

</aside>

### Task

Implement the `Data Polling` and `Data Processing` from Part 1. You can ignore the job scheduling for the implementation and focus on on-demand data fetching. Focus on querying the `Mock API Service`, storing the data persistently and calculating the performance metrics.

For storing the data you may use a different database than the one you mentioned in the system design for simplicity (you can use an in-memory database like SQLite or Redis for your solution, which can be set up in minutes).

You are given access to a `Mock API Service` providing raw performance data. You can access the service via the following base url: `https://datads-mock-ad-apis.happygrass-47d99234.germanywestcentral.azurecontainerapps.io`. There is a dedicated section below with full documentation about this service. Read it carefully.

For the implementation you should focus on querying and storing data from **1 platform** with a date range of `Last 30 Days`. However, make your implementation extensible to support the other platforms and larger date ranges as well. You will be asked about the extensibility in the interview.

**Important:** Your implementation should handle the following:

- API pagination (all platforms use different pagination methods)
- Rate limiting and retry logic with exponential backoff
- Data deduplication (same ad data might be fetched multiple times)
- Error handling for network failures and API errors

Bonus: Prepare a testing strategy by implementing key tests OR providing detailed testing plan

### Technical Constraints

- Use **JavaScript, TypeScript** or **Python** (your choice)
- Don't worry too much about data storing: Use any in-memory datastore for fast setup. Don't waste your time on setting up the ideal database.
- Include basic error handling and logging

### Deliverables

- Implementation of the data polling and data processing logic as `.py`, `.ts` or `.js` files
- Short documentation on how to run them (README.md)
- Sample output showing calculated metrics (CTR, CPC, ROAS)
- (Bonus) Testing strategy

## Part 3 — Implement Query API Layer *(Optional - Bonus)*

<aside>
⚠️

**Note:** This part is optional. Focus your time on Parts 1 and 2. Only attempt this if you have extra time and want to showcase additional skills.

</aside>

In this optional part, you can implement the `Query API Layer` from Part 1. Set up a basic API server using `express.js` or `fastapi`. The API server should expose the following 2 routes:

### API Endpoints

### `GET /api/performance`

**Parameters:**

- `platform` (optional): Filter by platform (e.g., "facebook", "google", "tiktok")
- `date_from` (optional): Start date in YYYY-MM-DD format
- `date_to` (optional): End date in YYYY-MM-DD format
- `campaign_id` (optional): Filter by specific campaign

**Response:**

```json
{
  "data": {
    "total_impressions": 50000,
    "total_clicks": 1200,
    "total_spend": 500.75,
    "total_revenue": 2400.00,
    "average_ctr": 0.024,
    "average_cpc": 0.417,
    "average_roas": 4.79
  },
  "filters_applied": {
    "platform": "facebook",
    "date_from": "2025-01-01",
    "date_to": "2025-01-31"
  }
}

```

### `GET /api/top-performing`

**Parameters:**

- `metric` (required): Sort by metric ("ctr", "cpc", "roas", "clicks", "revenue")
- `order` (optional): Sort order ("asc" or "desc", default: "desc")
- `limit` (optional): Number of results (default: 10, max: 100)
- `platform` (optional): Filter by platform
- `date_from` (optional): Start date in YYYY-MM-DD format
- `date_to` (optional): End date in YYYY-MM-DD format

**Response:**

```json
{
  "data": [
    {
      "ad_id": "fb_ad_456",
      "campaign_id": "fb_camp_123",
      "platform": "facebook",
      "date": "2025-01-15",
      "impressions": 10000,
      "clicks": 150,
      "spend": 75.50,
      "revenue": 360.00,
      "ctr": 0.015,
      "cpc": 0.503,
      "roas": 4.768
    }
  ],
  "pagination": {
    "limit": 10,
    "total": 150
  }
}

```

Both endpoints should include:

- Basic input validation with appropriate error messages
- Proper HTTP status codes
- Error handling for invalid parameters

To return the results you should utilize the data store from Part 2. Use the implementation from Part 2 to fill the data store with some data. You don't need to worry about production-ready monitoring/alerting, complex authentication systems, or extensive configuration options. Focus on setting up the API server, validating inputs and returning the requested data.

Bonus: Prepare a testing strategy by implementing key tests OR providing detailed testing plan

Bonus: Deploy the API to any cloud platform

### Technical Constraints

- Use **JavaScript, TypeScript** or **Python** (your choice)
- Include basic error handling and logging

### Deliverables

- Implementation of the API server and routes as `.py`, `.ts` or `.js` files
- Short documentation on how to run the API server (README.md)
- Example API calls with curl commands or a simple test script
- (Bonus) Testing strategy
- (Bonus) Deployment URL

## Part 4 — Submission

- Create a public git repository
- Upload your solution using the following folder structure (Use README files for any documentation)
    
    ```
    - part_1/
      - system_design.<png|jpg|pdf>
      - README.md (architectural explanation)
    - part_2/
      - README.md
      - <implementation_files>.<py|ts|js>
      - requirements.txt or package.json (if applicable)
    - part_3/
      - README.md
      - <implementation_files>.<py|ts|js>
      - requirements.txt or package.json (if applicable)
    - README.md (main project overview)
    
    ```
    
- Send the public url of the github repository to daniel@datads.io
    - Double check the git repository is public
    - Double check you added all necessary files to the repository
    - Mention your name and role in the email (so that we know to whom the repository belongs to)
    - Send **latest** 24 hours before the interview

## Mock API Service

**API Base URL:** `https://datads-mock-ad-apis.happygrass-47d99234.germanywestcentral.azurecontainerapps.io`

We provide a running mock API service that simulates the three ad platforms. Your task is to build a system that polls these APIs periodically and processes the data.

<aside>
⚠️

**Important Notes:**

- All APIs require authentication headers as specified below
- Each platform has different rate limits and error rates
- APIs return paginated results - you must handle pagination correctly
- Some endpoints may return 5xx errors randomly to simulate real-world conditions
</aside>

### Platform A API (Facebook-like)

```
GET {API_BASE_URL}/api/v1/campaigns/{campaign_id}/insights
Headers: x-api-key: facebook_test_key_123
Query Parameters:
- since: date (YYYY-MM-DD)
- until: date (YYYY-MM-DD)
- limit: number (max 100, default 25)
- after: pagination cursor

Rate Limit: 200 requests/hour
Intentional Errors: 5% random 500 errors + rate limiting

Response:
{
  "data": [
    {
      "campaign_id": "fb_camp_123",
      "ad_id": "fb_ad_456",
      "date": "2025-01-15",
      "impressions": 10000,
      "clicks": 150,
      "spend": 75.50,
      "conversions": 12,
      "revenue": 360.00
    }
  ],
  "paging": {
    "next": "25" // cursor for next page
  }
}

```

**Available Campaign IDs:** fb_camp_123, fb_camp_456, fb_camp_789

### Platform B API (Google-like)

```
GET {API_BASE_URL}/api/reports/campaigns
Headers: Authorization: Bearer google_test_token_456
Query Parameters:
- start_date: date (YYYY-MM-DD)
- end_date: date (YYYY-MM-DD)
- page_size: number (max 50, default 20)
- page_token: string

Rate Limit: 100 requests/hour
Intentional Errors: 5% random 500 errors + rate limiting

Response:
{
  "reports": [
    {
      "campaignId": "goog_123",
      "adGroupId": "goog_ag_456",
      "adId": "goog_ad_789",
      "date": "2025-01-15",
      "metrics": {
        "impressions": 8500,
        "clicks": 120,
        "cost": 60.25,
        "conversions": 8,
        "conversionValue": 240.00
      }
    }
  ],
  "nextPageToken": "40" // token for next page
}

```

**Note:** For Google API, `cost` maps to `spend` and `conversionValue` maps to `revenue` in your data model.

### Platform C API (TikTok-like)

```
GET {API_BASE_URL}/v1/ad/performance
Headers: Authorization: Bearer tiktok_test_token_789
Query Parameters:
- date_from: date (YYYY-MM-DD)
- date_to: date (YYYY-MM-DD)
- offset: number (default 0)
- limit: number (max 25, default 15)

Rate Limit: 50 requests/hour
Intentional Errors: 5% random 500 errors + rate limiting

Response:
{
  "performance_data": [
    {
      "campaign": {
        "id": "tt_camp_999",
        "ad_id": "tt_ad_888"
      },
      "performance": {
        "date": "2025-01-15",
        "views": 12000,
        "engagements": 180,
        "budget_spent": 90.00,
        "purchases": 15,
        "purchase_value": 450.00
      }
    }
  ],
  "has_more": true,
  "offset": 25
}

```

**Note:** For TikTok API, `views` maps to `impressions`, `engagements` maps to `clicks`, `budget_spent` maps to `spend`, and `purchase_value` maps to `revenue` in your data model.

### API Testing & Monitoring

```
GET {API_BASE_URL}/health
GET {API_BASE_URL}/rate-limits

```

The `/health` endpoint shows available endpoints and authentication details.
The `/rate-limits` endpoint shows current rate limit status for all platforms.

**Recommendation:** Start by testing these endpoints to ensure the API is accessible and understand the expected data structure.

## Evaluation Focus Areas

- **API Integration:** How well do you handle external API polling, pagination, and rate limits?
- **Data Processing:** Proper calculation of metrics and handling of different data formats
- **System Design:** How well do you structure the application for reliability, scalability and performance?
- **Data Modeling:** Appropriate database choices and schema design for time-series data
- **Code Quality:** Clean, maintainable, well-structured code with proper separation of concerns
- **Error Handling:** Robust handling of API failures, network issues, and edge cases
- **Documentation:** Clear explanation of your approach and how to run your code

## What We're NOT Looking For

- Perfect UI/frontend (focus on backend/API)
- Production-ready monitoring/alerting
- Complex authentication systems
- Extensive configuration options
- Over-engineering - keep it simple and focused

## Usage of AI Tools

- ✅ **Allowed:** Using LLMs (ChatGPT, Claude, etc.) for code assistance, debugging, documentation
- ❌ **Not Allowed:** Using application generators (Lovable, Replit Agent, etc.) that create the entire application
- **Requirement:** If you use AI assistance, briefly mention how in your documentation

## Questions?

Feel free to reach out to daniel@datads.io if you have any clarifying questions. We prefer seeing your interpretation and assumptions rather than perfect requirements.

**Note:** This exercise reflects real challenges you'd work on at DatAds. We're excited to see your approach!