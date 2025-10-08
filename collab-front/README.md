# collab-front

## Building with environment variables

To build with a custom domain, use the `BASE_DOMAIN` environment variable:

```bash
npm run build

# Build with custom domain
BASE_DOMAIN=your-domain.com npm run build:prod

# Or export the variable
export BASE_DOMAIN=your-domain.com
npm run build:prod
```

If the `BASE_DOMAIN` variable is not specified, the default domain `localhost` will be used.

You can also pass an argument to the `update_static.sh` script, which will be the suffix of the .env file (i.e., `./update_static.sh prod` will use `.env.prod`)