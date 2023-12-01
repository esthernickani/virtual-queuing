document.addEventListener("DOMContentLoaded", (e) => {
    /*initialise socket*/
    const socket = io({autoConnect: false});
    console.log(socket.connected)

    /*get elements for HTML*/
    const startQueueBtn = document.querySelector('#start_queue');
    const activateQueueForm = document.querySelector('.activate_queue');
    const activated = document.querySelector('#activate');
    const activateQueue = document.querySelector('#activate_queue')
    const showQueueBtn = document.querySelector('.show_queue_form')
    const joinQueueForm = document.querySelector('.join_queue_form')
    const submitJoinQueueForm = document.querySelector('#submit_join_queue_form')
    const organization = document.querySelector('.organizations')
    let organizationName;

    /*function to remove hidden class from form to reenter username */
    function displayActivateQueueForm(e) {
        console.log(e)
        e.preventDefault()
        activateQueueForm.classList.remove("hidden")
    }

    function displayCustomerJoinQueueForm() {
        joinQueueForm.classList.remove("hidden")
    }

    function connectOrgToSocket(e) {
        //function to connect organization to socket to activate queue
        e.preventDefault()
        /*get username and queuename from form */
        let checked = document.getElementById('activate').value;
        console.log(checked)

        /*Connect to socket if activated*/
        if (checked) {
            socket.connect();

            socket.emit('join')
        }
    }


    function connectCustomerToSocket(e) {
        //function to connect customer to socket to join queue

        console.log(e)
        e.preventDefault()
       
        /*get form data*/
        let firstName = document.getElementById('first_name').value;
        let lastName = document.getElementById('last_name').value;
        let email = document.getElementById('email').value;
        let contactNumber = document.getElementById('contact_number').value;
        let individualOrGroup = document.querySelector('input[name="size"]:checked').value;
        let groupSize = document.getElementById('group_size').value || null;

        socket.connect()
        
        socket.emit('join_queue', {
            firstName:firstName,
            lastName:lastName,
            email:email,
            contactNumber:contactNumber,
            organizationName:organizationName,
            groupSize : groupSize
        })
        
        
        
    }

    //on redirect socket should take the organization to the queue page
    socket.on('redirect_customer', function(destination) {
        console.log(destination)
        window.location.href = destination.url
    })


    /*check is the organization homepage is loaded  */
    if (startQueueBtn) {
        startQueueBtn.addEventListener('click', displayActivateQueueForm)
    }
    
    /*connect organization to socket*/
    if (activateQueue) {
        activateQueue.addEventListener('click', connectOrgToSocket)
    }

    //show form for customer to join
    if (showQueueBtn) {
        showQueueBtn.addEventListener('click', displayCustomerJoinQueueForm)
    }

    //connect customer to socket when clicked on submit form
    if (submitJoinQueueForm) {
        submitJoinQueueForm.addEventListener('click', connectCustomerToSocket)
    }

    //get organization name that customer wants to join queue
    if (organization) {
        organization.addEventListener('click', function(e) {
            organizationName = e.target.innerText
            displayCustomerJoinQueueForm()
            return;
        })
    }
})

