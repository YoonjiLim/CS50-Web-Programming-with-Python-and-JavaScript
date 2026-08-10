//Load posts when the page is loaded
document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector('#posts-container');
    if (container) {
        loadPosts(container.dataset.url);
    }

    const submitBtn = document.querySelector('#submit-post');
    if (submitBtn) {
        submitBtn.onclick = createPost;
    }
});


function loadPosts(url) {
    const postsContainer = document.querySelector('#posts-container');
    postsContainer.innerHTML = ''; // Prevent duplicate append when loading

    fetch(url)
    .then(response => response.json())
    .then(data => {

        //Clear pagination if there are no posts
        if (data.posts.length === 0) {
            postsContainer.innerHTML = 'No posts.';
            document.querySelector('#pagination').innerHTML = '';
            return;
        }
        
        data.posts.forEach(post => {
            const postDiv = document.createElement('div');
            
            postDiv.innerHTML = `
            <h3><a href="/profile/${post.user}">${post.user}</a></h3>
            <p class="post-content">${post.content}</p>
            <small>${post.timestamp}</small>
            <p class="likes-count">Likes: ${post.likes_count}</p>`;

            //Like button for authenticated users
            if (post.is_authenticated) {
                const likeBtn = document.createElement('button');
                likeBtn.textContent = post.liked_by_user ? 'Unlike' : 'Like';
                likeBtn.onclick = () => {
                    likePost(post, postDiv, likeBtn);
                };
                postDiv.append(likeBtn);
            }

            //Edit button for the owner of the post
            if (post.is_owner) {
                const editBtn = document.createElement('button');
                editBtn.textContent = 'Edit';
                editBtn.onclick = () => {
                    editPost(post, postDiv, editBtn); 
                };
                
                postDiv.append(editBtn);
            }
            
            postsContainer.append(postDiv);
        });

        renderPagination(data); //추가
    });
}


function getCSRFToken() {
    return document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
}//Updated


function createPost() {
    const content = document.querySelector('#post-content').value;
    if (!content.trim()) { //Prevent creating empty posts
        return;
    }

    fetch('/posts',{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            content: content
        })
    })
    .then(response => response.json())
    .then(data => {
        document.querySelector('#post-content').value = ''; // Clear the textarea
        
        const container = document.querySelector('#posts-container');
        loadPosts(container.dataset.url); //Reload after creating a new post
    });
}

function renderPagination(data){

    const paginationDiv = document.querySelector('#pagination');
    paginationDiv.innerHTML = '';
    
    const container = document.querySelector('#posts-container');
    const baseUrl = container.dataset.url;

    //Create previous button if there are prev pages. 
    if (data.has_previous) {
        const previousBtn = document.createElement('button');
        previousBtn.textContent = 'Previous';

        previousBtn.onclick = () => {
            loadPosts(`${baseUrl}?page=${data.current_page - 1}`);
        };
        paginationDiv.append(previousBtn);
    }

    //Current of total pages
    const currentPageNum = document.createElement('span');
    currentPageNum.textContent = `${data.current_page} of ${data.num_pages}`;
    paginationDiv.append(currentPageNum);

    //Create next button if there are next pages. 
    if (data.has_next) {
        const nextBtn = document.createElement('button');
        nextBtn.textContent = 'Next';
        
        nextBtn.onclick = () => {
            loadPosts(`${baseUrl}?page=${data.current_page + 1}`);
        };
        paginationDiv.append(nextBtn);
    }
}


function editPost(post, postDiv, editBtn) {
    const content = postDiv.querySelector('.post-content');
    const textarea = document.createElement('textarea');

    textarea.value = post.content;
    content.replaceWith(textarea);

    editBtn.textContent = 'Save';
    editBtn.onclick = () => {
        // Save the edited post
        fetch (`/editpost/${post.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                content: textarea.value
            })
        })
        .then(response => response.json())
        .then(data => {
            const container = document.querySelector('#posts-container');
            loadPosts(container.dataset.url); //Reload after editing
        });
    };
}

function likePost(post, postDiv, likeBtn) {

    fetch(`/likepost/${post.id}/like`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json', 
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        //DOM update
        const likes = postDiv.querySelector('.likes-count');
        likes.textContent = `Likes: ${data.likes_count}`;
        likeBtn.textContent = data.liked_by_user ? 'Unlike' : 'Like';
    });
}