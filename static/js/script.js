document.addEventListener("DOMContentLoaded", (e) => {
    /*initialise socket*/
    const socket = io({autoConnect: false});
    console.log(socket.connected)

    

    /*get elements for HTML*/
    const startQueueBtn = document.querySelector('#start_queue');
    const activateQueueForm = document.querySelector('.activate_queue');
    const activated = document.querySelector('#activate');
    const activateQueue = document.querySelector('#activate_queue');
    const showQueueBtn = document.querySelector('.show_queue_form');
    const joinQueueForm = document.querySelector('.join_queue_form');
    const submitJoinQueueForm = document.querySelector('#submit_join_queue_form');
    const organization = document.querySelector('.organizations');
    const getDirectionDiv = document.querySelector('.get_directions');
    const customerCode = document.querySelector('.customer_code');
    const leaveWaitlistBtn = document.querySelector('.leave_waitlist');
    const confirmLeaveNotif = document.querySelector('.confirm_leave');
    const phoneInputField = document.querySelector("#phone");
    const notificationsOrg = document.querySelector('.notifications')
    let phoneInput;
    if (phoneInputField) {
        phoneInput = window.intlTelInput(phoneInputField, {
        utilsScript:
        "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js",
        });
   } 
   let organizationName;

    /*function to remove hidden class from form to reenter username */
    function displayActivateQueueForm(e) {
        console.log('e')
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
        let contactNumber = phoneInput.getNumber();
        let individualOrGroup = document.querySelector('input[name="size"]:checked').value;
        let groupSize = document.getElementById('group_size').value || null;

        console.log(contactNumber)

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
        window.location.href = destination.url
    })

    function getCustomerLocation(e) {
        e.preventDefault()
        if (e.target.classList.contains('agree_btn')) {

            const successCallback = (position) => {
                console.log(position.coords.latitude)

                const dataToSend = {
                    'latitude': position.coords.latitude,
                    'longitude': position.coords.longitude
                }

                fetch(`/customer/${customerCode.textContent}/directions`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(dataToSend)
                })
            }

            const errorCallback = (error) => {
                console.log(error)
            }

            console.log(customerCode.textContent)

            navigator.geolocation.getCurrentPosition(successCallback, errorCallback, {
                enableHighAccuracy: true
            })
        }
    }

    function showLeaveWaitlistNotif(e) {
        e.preventDefault()
        confirmLeaveNotif.classList.remove("hidden")
    }

    /*intl phone number validation*/
    

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

    if (getDirectionDiv) {
        getDirectionDiv.addEventListener('click', getCustomerLocation)
    }
    
    if (leaveWaitlistBtn) {
        leaveWaitlistBtn.addEventListener('click', showLeaveWaitlistNotif)
    }

    //get organization name that customer wants to join queue
    if (organization) {
        organization.addEventListener('click', function(e) {
            organizationName = e.target.innerText
            displayCustomerJoinQueueForm()
            return;
        })
    }


    //check if password is same as confirm password
    const password = document.querySelector("#password")
    const confirmPassword = document.querySelector("#password_confirm")
    const message = document.querySelector("#message")

    if(password && confirmPassword) {
        confirmPassword.addEventListener("keyup", passConfirm)
    }
    

    function passConfirm(e) {
        e.preventDefault();
        if (password.value == confirmPassword.value) {
            message.style.color = "Green"
            message.textContent = "Passwords match"
        } else {
            message.style.color = "Red"
            message.textContent = "Passwords do not match"
        }
    }
})

