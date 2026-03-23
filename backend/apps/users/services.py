def update_user(user, data):
    if data.name is not None:
        user.name = data.name

    if data.bio is not None:
        user.bio = data.bio

    user.save()
    return user