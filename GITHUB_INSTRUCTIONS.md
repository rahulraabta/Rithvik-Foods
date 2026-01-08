# How to Push Your Website to GitHub

I have already prepared your files on your computer. You just need to send them to GitHub now.

## Step 1: Create the Repo
1.  Log in to [GitHub.com](https://github.com).
2.  Click the **+** (top right) -> **New repository**.
3.  Repository name: `rithvik-foods`
4.  Make it **Public**.
5.  **Do NOT** check "Add a README", "Add .gitignore", or "Choose a license". (Keep it empty).
6.  Click **Create repository**.

## Step 2: Push Your Code
You will see a screen with commands. **Copy and Run** these commands in your terminal (Command Prompt) inside the `Rithvik Foods` folder:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/rithvik-foods.git
git branch -M main
git push -u origin main
```
*(Replace `YOUR_USERNAME` with your actual GitHub username)*

## Step 3: Activate Website
1.  Once pushed, go to **Settings** (tabs at top of your repo).
2.  Click **Pages** (left sidebar).
3.  Under **Branch**, select `main` and click **Save**.
4.  Wait 1 minute, and your site will be live!
