# StudyPoint Gamification System

## 1. Purpose

StudyPoint gamification connects learning progress with two customization experiences:

- **Car Garage** — vehicles, paint, wheels, stickers and parts.
- **Character World** — BoZo characters, clothes, hair, shoes and accessories.

Learning is the only source of progression. Students earn XP and coins by answering questions, increasing SmartScore, reaching levels and maintaining a daily streak. Coins are then spent on the active game's collectible items.

## 2. Main values

| Value | Meaning |
| --- | --- |
| SmartScore | Topic mastery score from 0 to 100. Stored separately for every skill/topic. |
| XP | Permanent global learning experience. Determines the student's level. |
| Level | Global progression level from 1 to 12. |
| Coins | Shared currency used in both games. |
| Daily streak | Number of consecutive calendar days with at least one correct answer. |
| Longest streak | Highest daily streak the student has achieved. |
| Correct-answer streak | Session-level streak used only by SmartScore calculation. |
| Total problems solved | Number of correct rewarded answers. |

## 3. Answer flow

For every submitted practice answer:

1. The backend checks the answer.
2. SmartScore is recalculated for the current topic.
3. The gamification service processes the answer with a unique attempt ID.
4. If correct, the student receives 2 XP.
5. The service checks crossed SmartScore milestones.
6. The service recalculates the student's level.
7. Newly reached levels award coins.
8. The daily streak is updated.
9. A seven-day streak reward is issued when applicable.
10. Wallet, streak, milestone and transaction records are saved.
11. The final reward and updated balance are returned to the frontend.

The reward formula is:

```text
XP gained = correct ? 2 : 0

Coins gained =
    SmartScore milestone coins
  + level-up coins
  + seven-day streak coins
```

An ordinary correct answer currently gives no base coins. Question difficulty currently does not change XP or coin rewards.

## 4. SmartScore

SmartScore is calculated independently for every topic and stays between 0 and 100.

### Correct answers

Consecutive correct answers add progressively smaller amounts:

```text
1st correct answer:  +15
2nd correct answer:  +14
3rd correct answer:  +13
...
15th and later:      +1 minimum
```

Formula:

```text
correct streak after answer = previous correct streak + 1
SmartScore delta = max(1, 16 - correct streak after answer)
wrong-answer streak = 0
```

### Incorrect answers

Consecutive incorrect answers create progressively larger deductions:

```text
1st incorrect answer: -1
2nd incorrect answer: -2
3rd incorrect answer: -3
...
```

Formula:

```text
wrong streak after answer = previous wrong streak + 1
SmartScore delta = -wrong streak after answer
correct-answer streak = 0
```

### SmartScore zones

| Score | Zone |
| ---: | --- |
| 0–69 | Learning |
| 70–89 | Refining |
| 90–100 | Challenge |

### SmartScore coin milestones

| Milestone | Coins |
| ---: | ---: |
| 20 | 5 |
| 40 | 5 |
| 60 | 10 |
| 80 | 10 |
| 100 | 20 |

Milestones are awarded once per topic. Dropping below a milestone and reaching it again does not award it twice. If one answer crosses several new milestones, their rewards are added together.

## 5. XP and 12 levels

Every correct rewarded answer gives **2 XP**. Incorrect answers give no XP. XP is permanent and is not spent in the shop.

| Level | Total XP required | Level reward |
| ---: | ---: | ---: |
| 1 | 0 | Starting level |
| 2 | 300 | 100 coins |
| 3 | 700 | 100 coins |
| 4 | 1,200 | 100 coins |
| 5 | 1,800 | 100 coins |
| 6 | 2,500 | 100 coins |
| 7 | 3,300 | 100 coins |
| 8 | 4,300 | 100 coins |
| 9 | 5,500 | 100 coins |
| 10 | 7,000 | 100 coins |
| 11 | 8,800 | 100 coins |
| 12 | 10,900 | 100 coins |

The level is the highest level whose XP threshold has been reached. Level 12 is the maximum. Additional XP remains recorded after level 12.

Every level reward can be issued only once. If multiple levels are crossed in one operation, each newly crossed level awards 100 coins.

## 6. Daily streak

The daily streak is updated only by a correct answer.

```text
First correct day: streak becomes 1
Last correct day was yesterday: streak increases by 1
Already had a correct answer today: streak does not change
Missed at least one calendar day: streak restarts at 1
Incorrect answer: streak is unchanged
```

Dates use the backend's UTC date. The service also records the longest streak.

### Seven-day reward

Every completed seven-day cycle gives **50 coins**:

- day 7: 50 coins;
- day 14: another 50 coins;
- day 21: another 50 coins.

Each cycle has a unique database record, so refreshing or repeating a request cannot award it twice. Breaking the streak starts a new streak sequence.

## 7. Coins and wallet

Coins are shared between Car Garage and Character World.

### Coin income

- SmartScore milestones: 5–20 coins.
- Every new level: 100 coins.
- Every seven consecutive active days: 50 coins.

### Coin spending

Before a purchase, the backend verifies:

1. the item exists and is active;
2. the required level and XP have been reached;
3. the item is not already owned;
4. the student has enough coins;
5. the item belongs to the student's active game.

```text
new coin balance = current balance - item price
```

Selecting or equipping an already owned item costs nothing.

Every addition or deduction is written to wallet transaction history with its type, amount, resulting balance and reference object.

## 8. Vehicle progression

| Level | XP | Vehicle | Price |
| ---: | ---: | --- | ---: |
| 1 | 0 | Skateboard | Starter/100 |
| 2 | 300 | Scooter | 250 |
| 3 | 700 | Bicycle | 500 |
| 4 | 1,200 | Vino car | 900 |
| 5 | 1,800 | Sport motorcycle | 1,400 |
| 6 | 2,500 | Ducati motorcycle | 2,100 |
| 7 | 3,300 | Quad bike | 3,000 |
| 8 | 4,300 | Mini car | 4,200 |
| 9 | 5,500 | Ford Mustang | 6,000 |
| 10 | 7,000 | Jaguar sport car | 8,500 |
| 11 | 8,800 | McLaren supercar | 11,000 |
| 12 | 10,900 | Porsche hypercar | 13,500 |

Unlocking makes a vehicle available for purchase; it does not automatically make it owned. The skateboard is granted as the default vehicle.

## 9. Game selection

Before choosing a game, a new student can enter trial mode for both games:

1. customize a vehicle in Car Garage;
2. customize a BoZo avatar in Character World;
3. visit both experiences;
4. select one as the active game.

Trying a game does not change coins, XP, level or ownership. After selection, purchases and customization endpoints enforce the active game. Switching the active game does not delete progress or owned items.

## 10. Duplicate protection

Every practice attempt sends an idempotency key:

```text
practice_attempt:{attempt_id}
```

The backend stores the reward result against that key. If the same request is received again because of a double click, refresh or network retry, the stored result is returned without applying XP or coins again.

Additional unique database constraints protect:

- one SmartScore milestone history per student and topic;
- one level reward per student and level;
- one streak reward per streak sequence and seven-day cycle;
- one ownership record per student and item/vehicle.

## 11. Frontend synchronization

The backend database is the source of truth. The frontend Pinia store loads the current profile from:

```text
GET /gamification/me
```

The response includes level, XP, coins, streaks, next-level XP, vehicles, ownership, selected vehicle and garage items. After an answer or purchase, the frontend applies the returned reward immediately and then refreshes the profile when required.

XP progress within a level is calculated as:

```text
progress = (current XP - current level threshold)
           / (next level threshold - current level threshold)
           × 100
```

At maximum level, progress displays as 100%.

## 12. Currently inactive systems

The database contains models for achievements and daily missions, but the current reward processor does not yet award them automatically.

The API also returns `combo_streak = 0` and `combo_bonus = 0`. Therefore the active reward system currently has no session combo multiplier. This must not be confused with the correct-answer streak used by SmartScore or the calendar-based daily streak.

## 13. Main implementation files

- `backend/app/services/scoring.py` — SmartScore calculation.
- `backend/app/services/gamification_service.py` — XP, levels, coins, streaks, purchases and rewards.
- `backend/app/models/gamification.py` — wallet, streak, ownership and reward history tables.
- `backend/app/services/practice_service.py` — connects submitted answers to gamification.
- `src/stores/gamification.ts` — frontend gamification state.
- `src/api/gamification.ts` — frontend API requests.
