FROM apify/actor-node-playwright-chrome:20

COPY package.json ./
RUN npm install --omit=dev

COPY . ./

ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

CMD ["node", "src/main.js"]
