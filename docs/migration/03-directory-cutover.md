# Stage 3: Directory Cutover

Use this canonical feed for every step:

`https://shaqo88.github.io/enachmanson-feed/feed.xml`

Record the operator and exact cutover time in [STATUS.md](STATUS.md).

## 1. Configure the Podbean redirect

1. In Podbean, open **Settings → Feed → Advanced Feed Settings**.
2. Enter the canonical URL in **Redirect to a New Feed**.
3. Save the change.
4. Verify the old Podbean feed returns HTTP **301**, not 302.
5. Verify the `Location` header is the exact canonical URL, with no
   intermediate redirect.

Do not proceed if the old feed does not return the correct permanent redirect.

## 2. Update Spotify for Creators

1. Open the existing podcast in Spotify for Creators.
2. Go to **Settings**.
3. Select **Update** beside the current RSS feed.
4. Enter the canonical URL.
5. Confirm the hosting provider and complete Spotify's verification.

Update the existing show. Do not create or submit a duplicate show.

## 3. Confirm Apple Podcasts migration

Allow the Podbean 301 redirect and `itunes:new-feed-url` to migrate the existing
show.

1. Open the existing show in Apple Podcasts Connect.
2. Confirm that Apple recognizes the canonical feed.
3. Confirm that the show and its episodes remain attached to the existing
   listing.

Do not submit a new show.

## 4. Verify other directories

Check all known listings, including:

- Amazon Music
- Pocket Casts
- Overcast
- Castbox
- Podcast Index
- TuneIn
- Every directory recorded in the pre-cutover inventory

Allow each directory to follow the 301 redirect. Update its dashboard directly
only if it does not migrate automatically.

## 5. Test playback

In every major application:

- [ ] Play the oldest episode.
- [ ] Play the newest episode.
- [ ] Seek forward within each episode to exercise byte-range playback.
- [ ] Confirm there is one show listing, not a duplicate.
- [ ] Confirm there are no duplicate historical episodes.

## Exit gate

Stage 3 is complete when the old feed permanently redirects, Spotify and Apple
recognize the existing show at the canonical feed, other known directories have
been checked, and oldest/newest playback succeeds.
