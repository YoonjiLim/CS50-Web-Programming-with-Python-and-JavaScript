let current_mailbox = null;

document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');

  //Connect form submit 
  document.querySelector('#compose-form').onsubmit = function(event) {
    event.preventDefault();

    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
        recipients: document.querySelector('#compose-recipients').value,
        subject: document.querySelector('#compose-subject').value,
        body: document.querySelector('#compose-body').value
      })
    })
    .then(response => response.json())
    .then(result => {
      console.log(result);
      if (result.error) {
        alert(result.error);
      } else {
        load_mailbox('sent');
      }
    });
  };
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  current_mailbox = mailbox;
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    console.log(emails);

    if (emails.length === 0) {
      document.querySelector('#emails-view').innerHTML += `
      <p style="color:gray; margin-top:10px;">No emails in this mailbox.</p>`;
      return;
    }

    emails.forEach(email => {
      const div = document.createElement('div');
      div.style.border = "1px solid #ccc";
      div.style.padding = "8px";
      div.style.margin = "5px 0";
      div.style.cursor = "pointer";
      
      div.innerHTML = `
      <div style="display:flex; justify-content:space-between;">
      <div style="display:flex; gap:15px;">
      <span style="min-width:150px;"><strong>${email.sender}</strong></span>
      <span>${email.subject}</span>
      </div>
      <span>${email.timestamp}</span>
      </div>`;

      //Click event
      div.addEventListener('click', () => view_email(email.id));

      //Read or Unread
      if (email.read) {
        div.style.backgroundColor = "#e6e6e6a8";
      } else{
        div.style.backgroundColor = "white";
        div.style.fontWeight = "bold";
      }

      div.addEventListener('mouseover', () => {
        div.style.boxShadow = "0 2px 5px rgba(0,0,0,0.2)";
      });
      
      div.addEventListener('mouseout', () => {
        div.style.boxShadow = "none";
      });

      document.querySelector('#emails-view').append(div);
    });
  });
}

function view_email(id) {
  //Change view
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'block';

  //Get data
  fetch(`/emails/${id}`)
  .then(response => response.json())
  .then(email => {
    //Archive, Reply Button
    let button = '';
    if (current_mailbox === 'inbox') {
      button = `<button id="archive-btn" class="mail-btn archive-btn">Archive</button>`;
    } else if (current_mailbox === 'archive') {
      button = `<button id="archive-btn" class="mail-btn unarchive-btn">Unarchive</button>`;
    }
    button += `<button id="reply-btn" class="mail-btn reply-btn">Reply</button>`;

    //Render details
    document.querySelector('#email-view').innerHTML = `
    <p><strong>From:</strong> ${email.sender}</p>
    <p><strong>To:</strong> ${email.recipients.join(', ')}</p>
    <p><strong>Subject:</strong> ${email.subject}</p>
    <p><strong>Timestamp:</strong> ${email.timestamp}</p>
    <hr>
    <p style=" white-space: pre-line; margin-top:10px;">${email.body}</p>
    <div style="display:flex; justify-content:flex-end; gap:8px; margin-top:10px;">
    ${button}
    </div>`;

    //Archive event
    if (current_mailbox === 'inbox' || current_mailbox === 'archive') {
      document.querySelector('#archive-btn').addEventListener('click', () => {
        fetch(`/emails/${id}`, {
          method: 'PUT',
          body: JSON.stringify({
            archived: current_mailbox === 'inbox'
          })
        })
        .then(() => load_mailbox('inbox'));
      });
    }

    //Reply event
    document.querySelector('#reply-btn').addEventListener('click', () => {
      compose_email();
      document.querySelector('#compose-recipients').value = email.sender;

      let subject = email.subject;
      if (!subject.startsWith('Re:')) {
        subject = `Re: ${subject}`;
      }
      document.querySelector('#compose-subject').value = subject;

      const cleanedBody = email.body.replace(/^>+/gm, '');
      document.querySelector('#compose-body').value = 
      `\n\n-----------------------------------
On ${email.timestamp}, ${email.sender} wrote:

> ${cleanedBody.replace(/\n/g, '\n> ')}`;
    });

    //Mark as read
    fetch(`/emails/${id}`, {
      method: 'PUT',
      body: JSON.stringify({
        read: true
      })
    });
  });
}