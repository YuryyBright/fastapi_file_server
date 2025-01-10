# FastAPI Application Template

![GitHub Release](https://img.shields.io/github/v/release/seapagan/fastapi-template)
[![Ruff](https://github.com/seapagan/fastapi-template/actions/workflows/ruff.yml/badge.svg)](https://github.com/seapagan/fastapi-template/actions/workflows/ruff.yml)
[![Tests](https://github.com/seapagan/fastapi-template/actions/workflows/tests.yml/badge.svg)](https://github.com/seapagan/fastapi-template/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/seapagan/fastapi-template/branch/main/graph/badge.svg?token=IORAMTCT0X)](https://codecov.io/gh/seapagan/fastapi-template)
[![pages-build-deployment](https://github.com/seapagan/fastapi-template/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/seapagan/fastapi-template/actions/workflows/pages/pages-build-deployment)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/82085ec100b64e73bea63b5942371e94)](https://app.codacy.com/gh/seapagan/fastapi-template/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

Welcome to the **FastAPI Application Template**! This repository offers the **best solution for a file server API with user interface capabilities**. Built with FastAPI, it provides robust **authentication**, **authorization**, and **easy-to-use database management**. The template is designed with flexibility and performance in mind, perfect for developers needing a fast and secure way to build APIs with integrated user management.

### Key Features:
- **FastAPI Backend**: A high-performance API built with FastAPI.
- **Authentication & Authorization**: Built-in JWT-based security for user login, registration, and refresh tokens.
- **Database Integration**: PostgreSQL with SQLAlchemy ORM, providing an easy and asynchronous way to interact with the database.
- **Admin Command-Line Tool**: Easy management of users, settings, and server operations via the `Typer` CLI.
- **User Interface**: **Jinja templates** integrated with **Bootstrap** and **jQuery** for a clean, responsive front-end.
- **Docker Support**: Seamless Docker integration to develop and deploy your app in containers.
- **Testing Suite**: Built-in tests using `pytest` with automatic GitHub Actions for continuous testing.

This template also includes **file management** features, making it the ideal choice for projects that require file handling APIs with an intuitive user interface.

---

## Installation

To get started, click the 'Use this template' button on GitHub to create your own repository. Clone it to your local machine and begin development.

```bash
git clone https://github.com/YOUR_USERNAME/fastapi-template.git
cd fastapi-template
```

Ensure you have Python 3.9+ and install the necessary dependencies:

```bash
pip install -r requirements.txt
```

For containerized development, Docker is also supported.

```bash
docker compose up --build
```

---

## Docker

This template comes with Docker support for local development and testing:

1. **Run with Docker Compose**:

   ```bash
   docker compose up --build
   ```

2. **Run Migrations**:

   ```bash
   docker compose run --rm api alembic upgrade head
   ```

3. **Test the App**:

   ```bash
   docker compose run --rm api pytest
   ```

For more information, visit the full documentation [here](https://api-template.seapagan.net).

---

## Planned Functionality

Future versions will include:

- Expanded user management features
- File storage and retrieval API endpoints
- Integration with advanced third-party authentication providers

---

## Code Quality

This project emphasizes high-quality, maintainable code. We use `ruff` for static analysis, `pytest` for testing, and integrate `pre-commit` hooks to ensure clean code in every commit.

---

## Known Bugs

For a list of known bugs, please check the [BUGS.md](BUGS.md) file.

---

## Contributions

We welcome contributions! Check out the [Contributing Guidelines](https://api-template.seapagan.net/contributing/) for more details on how you can get involved.

---

## Contact & Discussions

If you have any questions or suggestions, feel free to start a discussion in our [GitHub Discussions](https://github.com/seapagan/fastapi-template/discussions) section.

Happy coding! 😊

---

**Note**: If this template helps your project, please consider acknowledging it in your project README and feel free to sponsor or buy a coffee! Your support is appreciated. 😃

[Sponsor my Work](https://github.com/sponsors/seapagan) | [Buy me a Coffee!](https://www.buymeacoffee.com/seapagan)