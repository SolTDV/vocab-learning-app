# Vocab Trainer

A smart vocabulary learning application using spaced repetition algorithm (SM-2) to optimize word retention and study efficiency.

## Features

- **Smart Study Scheduling**: Uses SM-2 spaced repetition algorithm to schedule reviews based on your performance
- **Dashboard**: See your progress, streak, XP, and daily targets at a glance
- **Study Sessions**: Interactive quiz mode with hint system and real-time feedback
- **Word Management**: Add, edit, and delete words with example sentences and notes
- **Analytics**: Track your learning progress with accuracy statistics, difficulty metrics, and activity heatmap
- **Progress Tracking**: Visual progress ring, study streaks, and achievement system
- **Dark Theme**: Beautiful, easy-on-the-eyes dark interface
- **Data Persistence**: All your vocabulary and progress is saved locally

## Getting Started

### Prerequisites
### Prerequisites

- Python 3.8 or higher
- tkinter (usually comes with Python)

**If tkinter is missing:**
```bash
# macOS
brew install python-tk

# Ubuntu/Debian
sudo apt-get install python3-tk

# Windows
# Included with Python installer

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd vocab-trainer
```

2. Run the application
```bash
python gui.py
```

The app will create the necessary data files automatically on first run.

## How to Use

### Adding Words

1. Go to the **"Manage Words"** tab
2. Enter a word, example sentence, and optional notes
3. Click **"+ Add Word"**
4. Your word is saved and ready to study!

### Study Sessions

1. Go to the **"Study"** tab
2. Set your target (number of words to study)
3. Click **"🚀 Start Study Session"**
4. For each word:
   - Read the sentence with the blank
   - Type the word you think fills the blank
   - Click **"Submit"** (or press Enter)
   - Rate your recall (1-4):
     - **1 = Again** (forgot it)
     - **2 = Hard** (barely remembered)
     - **3 = Good** (remembered it)
     - **4 = Easy** (instant recall)
5. Continue through the session
6. See your summary when done

### Keyboard Shortcuts

During study sessions:
- **Enter** - Submit answer
- **1, 2, 3, 4** - Rate recall (when enabled)
- **Hint button** - Reveal letters one by one

### Checking Progress

1. Go to the **"Statistics"** tab to see:
   - Overall accuracy percentage
   - Total reviews completed
   - Longest study streak
   - Words in each memory box (1-5)
   - Your most difficult words
2. Click **"📅 View Heatmap"** to see your 12-week study activity

## Understanding the Algorithm

This app uses the **SM-2 Spaced Repetition Algorithm**, which is scientifically proven to optimize learning.

### How It Works

1. **Ease Factor**: Adjusts based on how well you recall each word
2. **Interval**: Determines when you should review next
3. **Priority**: Words you struggle with appear more frequently

### Memory Boxes

Words progress through 5 boxes:
- **Box 1**: New words (review frequently)
- **Box 2**: Learning (review every 3 days)
- **Box 3**: Intermediate (review weekly)
- **Box 4**: Proficient (review every 2 weeks)
- **Box 5**: Mastered (review monthly)

## Project Structure

```
vocab-trainer/
├── gui.py          # Main UI application
├── core.py         # Core logic & algorithms
├── vocab.json              # Your vocabulary database
├── progress.json           # Your progress data
├── stats.json              # Your statistics
└── README.md               # This file
```



### Customization

You can customize colors and behavior by editing the `Colors` class in `gui_improved.py`:

```python
class Colors:
    PRIMARY = "#3b82f6"        # Change primary button color
    SUCCESS = "#10b981"        # Change success color
    TEXT_PRIMARY = "#60a5fa"   # Change text color
    # ... etc
```

## Data & Privacy

- All data is stored **locally** on your computer
- No account creation required
- No data is sent to external servers
- Your vocabulary is entirely under your control

## Troubleshooting

### App won't start
- Make sure you have Python 3.7+ installed
- On Linux: `apt-get install python3-tk`
- On macOS: Should come with Python

### Data disappeared
- Check that `vocab.json` still exists in the project folder
- If deleted, it will start fresh next time
- You can export your words using CSV feature (if implemented)

### Text is hard to read
- Colors are customizable in the `Colors` class
- Try adjusting `TEXT_PRIMARY` color
- Default colors are optimized for dark environments

## Future Features

- Replacing current File storage (JSON) with SQL database
- Web version
- Incorporating API
## 💡 Contributing

Found a bug or have a suggestion? 
- Create an issue in the repository
- Submit a pull request with improvements
- Share feedback and ideas


## 📄 License

This project is open source and available under the MIT License.


## 🙏 Acknowledgments

- SM-2 Algorithm by Piotr Wozniak
- Inspired by Anki and Quizlet
- Built with Python and Tkinter


*Last updated: February 2026*