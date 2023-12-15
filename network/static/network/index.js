    document.querySelector('#newPost').onsubmit = handlePost;
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const username = document.querySelector('.username').innerHTML
    let navigation = document.querySelector('.navigation')
    let postsContainer = document.querySelector('#container')
    const followPosts = document.querySelector('#followPosts')
    const profile = document.querySelector('#profile')
    const followPeople = document.querySelector('.followPeople')
    followPeople.addEventListener('click', following)
    document.addEventListener('click', (event) => {
        if (event.target.className == 'username') {
            userProfile(event.target.innerHTML);
        }
    })
    loadPosts(1)

async function handlePost(event) {
    event.preventDefault()

    // Get the CSRF token from the form
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Set the CSRF token cookie
    document.cookie = csrftoken;

    // Submit the data to the server
    const content = document.querySelector('.content').value;
    let response = await fetch('newPost', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            content: content,
        }),
    });

    let data = await response.json();

        //if the user not logged in, redirect them to the login page
    if (data.loggedout) {
        window.location.href = '/login'
    }
}


function displayError(error, place) {
    const div = document.createElement('div')
    div.className = 'error'
    div.innerHTML = `<h1>${error}</h1>`
    place.append(div)
}

async function loadPosts(num) {
    profile.style.display = 'none'
    let response = await fetch(`/posts?page=${num}`)
    let data = await response.json()
    removePosts(postsContainer)
    if (data.error) {
        displayError(data.error, postsContainer)
        return
    }
    data.posts.forEach((post) => {
        displayPost(post, postsContainer, data.liked_posts)
    })

    createNavigatin(data)
}

function createNavigatin(data) {
    navigation.style.display = 'block'
    let pagNavigation = document.querySelector('.navigation .list')
    let lists = ''
    if(data.current_page == 1) {
        lists = `
            <li class="page-item previous disabled">
                <a class="page-link" href="#">Previous</a>
            </li>
        `
    } else {
        lists = `
            <li class="page-item previous change">
                <a class="page-link" href="#">Previous</a>
            </li>
        `
    }


    let nav = ''
    for(let i=0; i < data.num_pages; i++) {
        if(i+1 === parseInt(data.current_page)) {
            nav = `
            <li class="page-item active" aria-current="page">
                <span class="page-link">${i+1}</span>
            </li>
        ` 
        }
        else {
            nav = `
                <li class="page-item disabled">
                    <span class="page-link">${i+1}</span>
                </li>
            ` 
        }
        lists += nav
    }
    if (data.current_page == data.num_pages) {
        lists += `
        <li class="page-item next disabled">
            <a class="page-link" href="#">next</a>
        </li>
    `
    } else {
        lists += `
        <li class="page-item next change">
            <a class="page-link" href="#">next</a>
        </li>
    `
    }
    pagNavigation.innerHTML = lists
    const changes = pagNavigation.querySelectorAll('.change')
    changes.forEach((element) => {
        element.addEventListener('click', () => {
            if (element.classList.contains('next')) {
                data.current_page++
                loadPosts(data.current_page)
            } else {
                data.current_page--
                loadPosts(data.current_page)
            }
        })
    })
}

function displayPost(post, place, liked_posts) {
let element = document.createElement('div')
    element.className = 'post';
    element.innerHTML = `
    <input type=hidden value=${post.id}>
    <h3 class="username">${post.user.username}</h3>
    <div class='content'>${post.content}</div>
    <div>${post.date}</div>
    <span class="material-symbols-outlined unliked">thumb_up</span>
    <div>comment</div>
    `


    handleLike(post.id ,liked_posts, element.querySelector('span'))

    if (post.user.username === username) {
        let div = document.createElement('div')
        div.innerHTML = `<span>Edit</span>`
        div.className = 'edit'
        element.append(div)

        div.addEventListener('click', () => {
            handleEdit(post, element.querySelector('.content'))
        })
    }
    place.append(element)
}

function handleLike(post, liked_posts, place) {
    if (liked_posts.includes(post)) {
        place.classList.add('liked')
        place.classList.remove('unliked')
    }

    place.addEventListener('click', () => {
         addLike(post, place)
    })
}

async function addLike(id, place) {
    let response = await fetch('/addLike', {
        method: 'PUT',
        headers: {
            'x-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            'postId': id, 
        })
    })
    let data = await response.json()
    if (data.success) {
        place.classList.toggle('liked')
            //if the user not logged in, redirect them to the login page
    } else if (data.loggedout) {
        window.location.href = '/login'
    }
} 

function removePosts() {
    let children = Array.from(postsContainer.children).slice(2)
    children.forEach((child) => {
        child.remove()
    })
}

async function userProfile(username) {
    navigation.style.display = 'none'
    postsContainer.style.display = 'none'
    followPosts.style.display = 'none'

    if (profile.style.display == 'none') {
        let response = await fetch(`user/${username}`)
        let data = await response.json()
        if (data.loggedout) {
            window.location.href = '/login'
        }
        let file = data
        profile.querySelector('.username').innerHTML = `All ${username} Posts`
        if (file.followStatus[0]) {
            followBtn = document.createElement('button')
            followBtn.className = 'btn btn-primary follow-btn'
            followBtn.setAttribute('type', 'button')  
            followBtn.innerHTML = file.followStatus[1] ? 'follow' : 'unfollow'   
            profile.firstElementChild.append(followBtn) 

            followBtn.addEventListener('click', () => {
                handleFollow(username, file)
            })
        }
        profile.querySelector('.follows').innerHTML = `follows: <span>${data.follows}</span>`
        profile.querySelector('.followers').innerHTML = `followers: <span>${data.followers}</span>`
        allposts = data.posts.posts
        allposts.forEach((post) => {
            displayPost(post, profile, data.liked_posts)
        })
    }
    profile.style.display = 'block'
}

async function handleFollow(username, file) {
    csrfToken = profile.querySelector('[name=csrfmiddlewaretoken]').value
    let response = await fetch('handleFollow', {
        method: 'PUT', 
        headers: {
            'X-CSRFToken': csrfToken,
        },
        body : JSON.stringify({
            username : username,
            followstatus : file.followStatus[1]
        })
    })
    let data = await response.json()

    if (data.sucess) {
        file.followStatus[1] = !(file.followStatus[1])
        updateFollowDisplay(file.followStatus[1])
    } 

        //if the user not logged in, redirect them to the login page

    if (data.loggedout) {
        window.location.href = '/login'
    }
}

function updateFollowDisplay(followStatus) {
    profile.querySelector('.follow-btn').innerHTML = followStatus ? 'follow' : 'unfollow' 
    profile.querySelector('.followers').querySelector('span').innerHTML = followStatus ? parseInt(profile.querySelector('.followers').querySelector('span').innerHTML) - 1 : parseInt(profile.querySelector('.followers').querySelector('span').innerHTML) + 1; 
}

async function following(e) {
    let response = await fetch('following')
    let data = await response.json()

    //if the user not logged in, redirect them to the login page
    if (data.loggedout) {
        window.location.href = '/login'
    }

    data.posts.forEach((post) => {
        displayPost(post, followPosts, data.liked_posts)
    } )

    navigation.style.display = 'none'
    postsContainer.style.display = 'none'
    profile.style.display = 'none'
    followPosts.style.display = 'block'
}

function handleEdit(post, place) {
    place.innerHTML = `<div class="form-floating">
                            <textarea class="form-control" placeholder="Write New Post here" id="floatingTextarea2" style="height: 50px"></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary disabled">Save</button>
                      `
    const button = place.querySelector('button')
    const textarea = place.querySelector('textarea')

    textarea.addEventListener('input', () => {
        if (textarea.value) {
            button.classList.remove('disabled')
        } else {
            button.classList.add('disabled')
        }
    })

    button.addEventListener('click', () => {
        if(!(button.classList.contains('disabled'))) {
            Edit(post, textarea.value, place)
        }
    })
}

async function Edit(post, newPost, place) {
    let response = await fetch('/Edit', {
        method: 'PUT',
        headers: {
            'x-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            'postId': post.id,
            'newPost' : newPost,
        })
    })

    let data = await response.json()
    if (data.success) {
        place.innerHTML = `
            <div class='content'>${newPost}</div>
        `
    }

    //if the user not logged in, redirect them to the login page
    if (data.loggedout) {
        window.location.href = '/login'
    }
}