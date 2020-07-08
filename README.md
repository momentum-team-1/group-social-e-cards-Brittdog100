# CardClub API
It's an API.

## Endpoints

`api/` - The root API endpoint isn't super useful, but it exists.

### Card Endpoints

`api/feed/` - Returns a paginated feed of cards from users you follow as JSON.

`api/card/` - Operates on the platonic ideal of a card.

 - `GET`: gets a list of all cards, paginated
 - `POST`: submits a card. Required fields are two strings, `text_inner` and `text_outer`.

`api/card/mine/` - Returns a list of cards including those authored by the current user, and those that tag the current user.

`api/card/<int:pk>/` - Operates on a specific card that Plato may or may not approve of.

- `GET`: returns information about the card.
- `DELETE`: deletes the card. Poor card.

`api/card/<int:pk>/comment/` - Operates on a card's comments.

- `GET`: returns all comments on a card
- `POST`: submits a comment on a card
- `DELETE`: deletes a comment. This can only be done by the comment's author, and requires an int `id` to be sent with the request as JSON.

### User Endpoints

`api/user/` - Does user-related things that are user-ful. I'm extremely funny.

- `GET`: returns a list of all users
- `POST`: creates a new user

`api/user/<str:username>/` - Returns information on a specific user.

`api/user/<str:username>/cards/` - Returns all cards authored by a given user.

`api/user/<str:username>/friend/` - Operates on the relationship with the currently logged in user

- `GET`: returns an integer representing the relationship: 0 for no relation; 1 means the logged in user follows the target; 2 means the target follows the logged in user; 3 means the users are friends. The integer is a two bit number, where the first bit represents whether the logged in user follows the target, and the second bit represents whether the target follows the logged in user.
- `POST`: makes the logged in user follow the target
- `DELETE`: makes the logged in user unfollow the target

`api/user/<str:username>/friend_list/` - Returns a list of all users the target is following.