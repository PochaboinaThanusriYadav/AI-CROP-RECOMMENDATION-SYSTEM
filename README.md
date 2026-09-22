# AI Crop Recommendation System

This project provides three independent crop-advisory pathways:

- Soil image classification with the MobileNetV2 model.
- Location-based recommendations using Telangana historical crop data.
- Questionnaire recommendations using a transparent weighted scoring algorithm.

## Questionnaire Recommendation

The questionnaire algorithm in `backend/questionnaire_recommender.py` uses the selected district, mandal, and season. Its score is composed of:

- 50% historical cultivation score
- 20% irrigation and water suitability
- 15% land or soil suitability
- 10% season suitability
- 5% farmer preference, including previous crop and duration

The endpoint is `POST /questionnaire/recommendation`.

## Weather And Planting Advisory

`GET /weather` fetches current weather and a four-day forecast from Open-Meteo. The advisor in `backend/planting_advisor.py` evaluates temperature, rainfall, humidity, and wind for each forecast day. `POST /planting-advisory` returns a suitability status, score, recommended days, and reasons.

These are transparent generic weather-suitability rules, not crop-specific agronomic predictions. Copernicus satellite integration and crop-specific thresholds are not implemented.

The Results page keeps questionnaire and GPS/location recommendations separate and displays the weather-based planting advisory when location weather data is available.

## Running Locally

From the project root:

```bash
npm install
npm run dev
```

From `backend/` after installing `backend/requirements.txt`:

```bash
python app.py
```

Set `VITE_API_BASE_URL` to the Flask server URL in `.env` before using the frontend API calls.
## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and Oxlint's TypeScript related rules in your project.
