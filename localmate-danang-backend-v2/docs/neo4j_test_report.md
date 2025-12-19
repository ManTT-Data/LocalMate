# Neo4j Category Filter Test Report

**Date**: 2025-12-15

## Test Coordinates

| Test Case | Latitude | Longitude | Max Distance (km) |
|-----------|----------|-----------|-------------------|
| Case 1 | 16.0626442 | 108.2462143 | 18.72 |
| Case 2 | 16.0623184 | 108.2306049 | 17.94 |

## Results by Category

| Category | Case 1 | Case 2 |
|----------|:------:|:------:|
| restaurant | 10 | 10 |
| coffee | 10 | 10 |
| bar | 10 | 10 |
| seafood | 4 | 4 |
| steak | 3 | 3 |
| gym | 3 | 3 |
| hotel | 1 | 1 |
| attraction | 0 | 0 |
| spa | 0 | 0 |

---

## All Available Categories (69 total)

### 🍜 Ăn uống (Food & Drink)
| Category | Category | Category |
|----------|----------|----------|
| Asian restaurant | Bakery | Bar |
| Bistro | Breakfast restaurant | Cafe |
| Cantonese restaurant | Chicken restaurant | Chinese restaurant |
| Cocktail bar | Coffee shop | Country food restaurant |
| Deli | Dessert shop | Dumpling restaurant |
| Espresso bar | Family restaurant | Fine dining restaurant |
| Food court | French restaurant | Hamburger restaurant |
| Hot pot restaurant | Ice cream shop | Indian restaurant |
| Irish pub | Italian restaurant | Izakaya restaurant |
| Japanese restaurant | Korean BBQ restaurant | Korean restaurant |
| Live music bar | Malaysian restaurant | Mexican restaurant |
| Noodle shop | Pho restaurant | Pizza restaurant |
| Ramen restaurant | Restaurant | Restaurant or cafe |
| Rice cake shop | Sandwich shop | Seafood restaurant |
| Soup shop | Sports bar | Steak house |
| Sushi restaurant | Takeout Restaurant | Tiffin center |
| Udon noodle restaurant | Vegan restaurant | Vegetarian restaurant |
| Vietnamese restaurant | | |

### 🏨 Lưu trú (Accommodation)
- Hotel
- Holiday apartment rental

### 🏃 Thể thao (Sports)
- Athletic club
- Badminton court
- Fitness center
- Gym
- Pickleball court
- Soccer field
- Sports club
- Sports complex
- Tennis court

### 🎮 Giải trí (Entertainment)
- Board game club
- Disco club
- Game store
- Movie theater
- Musical club

---

## API Usage

```bash
POST /api/v1/nearby
{
  "lat": 16.0626442,
  "lng": 108.2462143,
  "max_distance_km": 5,
  "category": "coffee"
}
```

> **Note**: Category filter sử dụng `CONTAINS` nên chỉ cần keyword (vd: `coffee` match `Coffee shop`).
