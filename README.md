# OOP-JSON-Data-Management-

OOP JSON Data Management practice and example.

This a sameple data management example usin JSONs for practicing OOP in python and showing some good practices to some friends.

## Instructions

- Install pipenv
- Install the repo
- Use username: `alfredo`, password: `alfredo888` to log in as the already existing user.
- Run only `main.py` to see the printed menu and options.
- To use commands, run them via CLI as shown below.

## Command Line Usage

**General Format:**

```
pipenv run python main.py [command] [subcommand] [options]
```

### User Commands

- **Create user:**
  ```
  pipenv run python main.py users create -n <username> -p <password>
  ```
- **Login:**
  ```
  pipenv run python main.py users login -n <username> -p <password>
  ```
- **Logout:**
  ```
  pipenv run python main.py users logout
  ```

### Task Commands

- **List tasks:**
  ```
  pipenv run python main.py tasks list-tasks
  ```
- **Create task:**
  ```
  pipenv run python main.py tasks create-task -t <title> -d <description>
  ```
- **Edit task:**
  ```
  pipenv run python main.py tasks edit-task -id <uuid> -t <title> -d <description> -s <status>
  ```
- **Delete task:**
  ```
  pipenv run python main.py tasks delete-task -id <uuid>
  ```

**Aliases:**

- Most commands have aliases (e.g., `add` for `create`, `mod` for `edit-task`, `del` for `delete-task`, etc.).

**Help:**

- To see all available commands and options:
  ```
  pipenv run python main.py --help
  pipenv run python main.py users --help
  pipenv run python main.py tasks --help
  ```
