# Telegram Bot Setup on Koyeb

This guide will walk you through setting up your Telegram bot on Koyeb.

## Prerequisites

1. **Python** installed on your local machine.
2. **Telegram Bot Token**: You can create a bot and get the token from [BotFather](https://t.me/BotFather) on Telegram.
3. **GitHub Account**: You will need a GitHub account to push your code.

## Step-by-Step Guide

### Step 1: Create a GitHub Repository

1. Go to your GitHub account and create a new repository for your bot code.
2. Clone the repository to your local machine.

### Step 2: Add Your Bot Code

1. Add your bot code (the Python script) to your repository.
2. Create a `.env` file in the root directory of your repository and add your bot token:
    ```env
    TELEGRAM_BOT_TOKEN=your_bot_token_here
    ```
3. Commit and push the changes to your GitHub repository.

### Step 3: Deploy to Koyeb

1. Log in to your [Koyeb](https://www.koyeb.com) account or create a new account if you don't have one.
2. Click on the `Create App` button.
3. Select `GitHub` as your deployment source and connect your GitHub account.
4. Choose the repository where you pushed your bot code.
5. Configure the build settings:
    - **Runtime**: Select `Python`
    - **Build Command**: `pip install -r requirements.txt`
    - **Start Command**: `python your_bot_script.py`
6. Add environment variables:
    - Key: `TELEGRAM_BOT_TOKEN`
    - Value: `your_bot_token_here`
7. Click on `Create App` to deploy your bot.

### Step 4: Monitor and Manage Your Bot

1. After deployment, you can monitor your bot's logs and performance from the Koyeb dashboard.
2. Make sure to update your code and redeploy if you make any changes.

### Additional Resources

- [Koyeb Documentation](https://docs.koyeb.com/)
- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

