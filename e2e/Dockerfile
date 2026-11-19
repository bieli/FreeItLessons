FROM mcr.microsoft.com/playwright:v1.65.1-noble
WORKDIR /e2e
COPY package.json package-lock.json ./
RUN npm ci
COPY playwright.config.js ./
COPY tests ./tests
CMD ["npx", "playwright", "test"]
