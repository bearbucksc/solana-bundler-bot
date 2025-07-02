document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    const statusElement = document.getElementById('status');
    const totalWallets = document.getElementById('total-wallets');
    const newWallets = document.getElementById('new-wallets');
    const activeWallets = document.getElementById('active-wallets');
    const retiredWallets = document.getElementById('retired-wallets');
    const activityLog = document.getElementById('activity-log');
    const bundleForm = document.getElementById('bundle-form');
    const transactionsInput = document.getElementById('transactions');

    // Add placeholder text for transactions input
    transactionsInput.placeholder = JSON.stringify([
        {
            "programId": "YourProgramId",
            "accounts": [
                { "pubkey": "YourPublicKey", "isSigner": true, "isWritable": true }
            ],
            "data": "YourData"
        }
    ], null, 2);

    // Add validation to transactions input
    transactionsInput.addEventListener('input', function() {
        try {
            JSON.parse(this.value);
            this.classList.remove('is-invalid');
            this.classList.add('is-valid');
        } catch (e) {
            this.classList.remove('is-valid');
            this.classList.add('is-invalid');
        }
    });

    // Handle connection status
    socket.on('connect', () => {
        statusElement.textContent = 'Connected';
        statusElement.classList.remove('status-red');
        statusElement.classList.add('status-green');
        statusElement.classList.add('fade-in');
    });

    socket.on('disconnect', () => {
        statusElement.textContent = 'Disconnected';
        statusElement.classList.remove('status-green');
        statusElement.classList.add('status-red');
        statusElement.classList.add('fade-in');
    });

    // Handle analytics updates
    socket.on('analytics', (data) => {
        totalWallets.textContent = data.total;
        newWallets.textContent = data.new;
        activeWallets.textContent = data.active;
        retiredWallets.textContent = data.retired;
        
        // Add animation to stats updates
        [totalWallets, newWallets, activeWallets, retiredWallets].forEach(el => {
            el.classList.add('fade-in');
            setTimeout(() => el.classList.remove('fade-in'), 500);
        });
    });

    // Handle bundle creation
    bundleForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const transactions = transactionsInput.value;
        
        // Validate input
        if (!transactions.trim()) {
            alert('Please enter transactions');
            return;
        }

        try {
            const response = await fetch('/api/bundle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ transactions: JSON.parse(transactions) }),
            });
            
            const data = await response.json();
            
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                // Add to activity log
                const entry = document.createElement('div');
                entry.className = 'activity-entry fade-in';
                entry.innerHTML = `
                    <span class="status-indicator ${data.success ? 'status-green' : 'status-red'}"></span>
                    ${new Date().toLocaleTimeString()} - Bundle ${data.signature.substring(0, 8)}...${data.signature.substring(-8)} ${data.success ? 'Success' : 'Failed'}
                `;
                activityLog.insertBefore(entry, activityLog.firstChild);
                
                // Scroll to top
                activityLog.scrollTop = 0;
                
                // Clear form
                transactionsInput.value = '';
            }
        } catch (error) {
            alert('Error: ' + error.message);
        }
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
