# Twittergram

This application takes messages from one of various sources, like a Twitter or Mastodon account, and
forwards them to a Telegram chat.

## Supported Sources

The following message sources are supported:

- A Twitter account's timeline ([see below](#twitter))
- A Mastodon account's timeline ([see below](#mastodon))
- A mailbox/folder in an email account with [JMAP protocol](https://jmap.io/) support
  ([see below](#email))

## Usage

The app requires Python 3.11+ and [Poetry](https://python-poetry.org/) 1.3.0+.

Install dependencies:

```
poetry install --without=dev
```

Once the dependencies are installed, you can run the app any of the following ways:

```
twittergram <command-name>
python -m twittergram <command-name>
poetry run twittergram <command-name>
```

The command name differs depending on whether you want to forward tweets, toots, or emails. The app
will forward all messages that were published since the last time it ran, you'll have to take care
of scheduling runs yourself, e.g. using a cron job. If the app never ran before, it'll forward the
ten most recent messages.

### Configuration

The app is configured using dotenv files and environment variables, the latter taking precedence.
If a file called `.env` exists, it will always be loaded. You can specify additional dotenv files to
load with the `--env` command line option:

```
twittergram --env mail forward-mails
```

In the example above, the `.env` file would be loaded, then the `.env.mail`. If any keys are present
in both files, the respective values from the `.env.mail` file take precedence. It's also possible
to load even more dotenv files by repeating the `--env` command line option:

```
twittergram --env mail --env override forward-mails
```

In that example, three dotenv files would be loaded (if they exist): `.env`, `.env.mail` and
`.env.override`. The last file you specify will have the highest precedence.

#### Required Configuration

The following configuration options must be set no matter your use case.

|            Key            |                  Example Value                   | Description                                                                                                                                                                                                                                                                                                                             |
|:-------------------------:|:------------------------------------------------:|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      `DOWNLOAD_DIR`       |          `/tmp/twittergram_downloads/`           | A directory that's used to download media files before uploading them to Telegram.                                                                                                                                                                                                                                                      |
|     `STATE_FILE_PATH`     |             `twittergram_state.json`             | The path to a file in which the app can store its state between runs. You must choose different paths for different commands/use cases.                                                                                                                                                                                                 |
| `TELEGRAM_TARGET_CHAT_ID` |                    `12345678`                    | The ID of the Telegram chat to which messages should be forwarded.                                                                                                                                                                                                                                                                      |
|     `TELEGRAM_TOKEN`      | `3145649874:ASDFSGLXCG-DSFHLFG4REKLJTHSDFVGCLXG` | A Telegram Bot API token.                                                                                                                                                                                                                                                                                                               |
| `TELEGRAM_UPLOAD_CHAT_ID` |                   `1259947317`                   | A chat where media files can be uploaded before sending them to the actual target chat. This is a measure to circumvent Telegram's size limit of 20 MB for file uploads: we upload single media files to the "upload chat" first and then use the resulting Telegram files IDs to send them as a media group to the actual target chat. |

### Twitter

To forward Tweets, first you'll have to register your application with Twitter in their
[Developer Portal](https://developer.twitter.com). Since this app doesn't authenticate on behalf
of any user, you can ignore most of the options and just create a Bearer token for your project.

The app won't forward replies and retweets.

#### Twitter Configuration Options

The following configuration options (in addition to [the ones above](#required-configuration)) are
required for Twitter.

|           Key            |          Example Value          | Description                                                                    |
|:------------------------:|:-------------------------------:|--------------------------------------------------------------------------------|
| `TWITTER_SOURCE_ACCOUNT` |            `elhotzo`            | The username of a (public) Twitter account whose messages you want to forward. |
|     `TWITTER_TOKEN`      | `AAAAAAAAAAAAAAAAAAAAAPvo[...]` | The Twitter API Bearer token you've obtained as described above.               |


### Mastodon

TODO: document this

### Email

TODO: document this

