(function () {
    // Currency list for African countries
    const currencies = {
        'DZD': { name: 'Algerian Dinar', country: 'Algeria' },
        'AOA': { name: 'Kwanza', country: 'Angola' },
        'XOF': { name: 'West African CFA Franc', country: 'WAEMU (BCEAO) countries' },
        'BWP': { name: 'Pula', country: 'Botswana' },
        'BIF': { name: 'Burundian Franc', country: 'Burundi' },
        'CVE': { name: 'Cape Verdean Escudo', country: 'Cabo Verde' },
        'XAF': { name: 'Central African CFA Franc', country: 'CEMAC countries' },
        'KMF': { name: 'Comorian Franc', country: 'Comoros' },
        'CDF': { name: 'Congolese Franc', country: 'Democratic Republic of the Congo' },
        'DJF': { name: 'Djiboutian Franc', country: 'Djibouti' },
        'EGP': { name: 'Egyptian Pound', country: 'Egypt' },
        'ERN': { name: 'Nakfa', country: 'Eritrea' },
        'ETB': { name: 'Ethiopian Birr', country: 'Ethiopia' },
        'GMD': { name: 'Gambian Dalasi', country: 'Gambia' },
        'GHS': { name: 'Ghanaian Cedi', country: 'Ghana' },
        'GNF': { name: 'Guinean Franc', country: 'Guinea' },
        'XAF': { name: 'Central African CFA Franc', country: 'Cameroon / Central African states' },
        'GIP': { name: 'Gibraltar Pound', country: 'Gibraltar' },
        'KES': { name: 'Kenyan Shilling', country: 'Kenya' },
        'LSL': { name: 'Loti', country: 'Lesotho' },
        'LRD': { name: 'Liberian Dollar', country: 'Liberia' },
        'LYD': { name: 'Libyan Dinar', country: 'Libya' },
        'MGA': { name: 'Malagasy Ariary', country: 'Madagascar' },
        'MWK': { name: 'Malawian Kwacha', country: 'Malawi' },
        'MGA': { name: 'Malagasy Ariary', country: 'Madagascar' },
        'MRO': { name: 'Ouguiya (old)', country: 'Mauritania' },
        'MRU': { name: 'Mauritanian Ouguiya', country: 'Mauritania' },
        'MUR': { name: 'Mauritian Rupee', country: 'Mauritius' },
        'MAD': { name: 'Moroccan Dirham', country: 'Morocco' },
        'MZN': { name: 'Mozambican Metical', country: 'Mozambique' },
        'NAD': { name: 'Namibian Dollar', country: 'Namibia' },
        'NGN': { name: 'Nigerian Naira', country: 'Nigeria' },
        'RWF': { name: 'Rwandan Franc', country: 'Rwanda' },
        'STN': { name: 'Dobra', country: 'Sao Tome and Principe' },
        'XOF': { name: 'West African CFA Franc', country: 'Senegal / West African states' },
        'SCR': { name: 'Seychellois Rupee', country: 'Seychelles' },
        'SLL': { name: 'Leone', country: 'Sierra Leone' },
        'SOS': { name: 'Somali Shilling', country: 'Somalia' },
        'ZAR': { name: 'South African Rand', country: 'South Africa' },
        'SSP': { name: 'South Sudanese Pound', country: 'South Sudan' },
        'SDG': { name: 'Sudanese Pound', country: 'Sudan' },
        'SZL': { name: 'Lilangeni', country: 'Eswatini' },
        'TZS': { name: 'Tanzanian Shilling', country: 'Tanzania' },
        'TND': { name: 'Tunisian Dinar', country: 'Tunisia' },
        'UGX': { name: 'Ugandan Shilling', country: 'Uganda' },
        'ZMW': { name: 'Zambian Kwacha', country: 'Zambia' },
        'ZWL': { name: 'Zimbabwean Dollar', country: 'Zimbabwe' },
        'CDF': { name: 'Congolese Franc', country: 'DRC' },
        'BWP': { name: 'Pula', country: 'Botswana' },
        'AOA': { name: 'Kwanza', country: 'Angola' },
        'TND': { name: 'Tunisian Dinar', country: 'Tunisia' },
        'XAF': { name: 'Central African CFA Franc', country: 'CEMAC' }
    };

    const mock = {
        '/v1/transactions/quote': {
            method: 'POST',
            schema: [
                { name: 'source_currency', placeholder: 'GHS', description: 'Source currency (3-letter code)', required: true },
                { name: 'target_currency', placeholder: 'KES', description: 'Target currency (3-letter code)', required: true },
                { name: 'amount', placeholder: '100', description: 'Amount to convert (numeric)', required: true }
            ],
            response: {
                quote_id: 'q_123456',
                source_amount: 100,
                target_amount: 520.45,
                rate: 5.2045,
                fees: 0.5,
                valid_for_seconds: 60,
                status: 'OK'
            }
        },
        '/v1/transactions/create': {
            method: 'POST',
            schema: [
                { name: 'quote_id', placeholder: 'q_123456', description: 'Quote identifier returned by /transactions/quote', required: true },
                { name: 'requote_expired', placeholder: 'false', description: 'Requote and create at new rate if the quote_id is expired', required: false },
                { name: 'sender_phone', placeholder: '+233xxxxxxxx', description: "Sender phone in E.164 format", required: true },
                { name: 'recipient_phone', placeholder: '+254yyyyyyyy', description: "Recipient phone in E.164 format", required: true }
            ],
            response: {
                transaction_id: 'tx_987654',
                status: 'PENDING',
                message: 'Funds locked, awaiting partner settlement'
            }
        },
        '/v1/transactions/{id}': {
            method: 'GET',
            schema: [
                { name: 'transaction_id', placeholder: 'tx_987654', description: 'Transaction ID to query (e.g. tx_987654)', required: true }
            ],
            response: {
                transaction_id: 'tx_987654',
                status: 'SETTLED',
                source_amount: 100,
                destination_amount: 520.45,
                created_at: '2025-11-23T10:30:00Z',
                settled_at: '2025-11-23T10:31:45Z',
                message: 'Transaction successfully settled'
            }
        },
        '/v1/partners': {
            method: 'GET',
            schema: [],
            response: [
                { id: 'mtngh', name: 'MTN Ghana', status: 'CONNECTED' },
                { id: 'mpesaken', name: 'M-Pesa Kenya', status: 'CONNECTED' }
            ]
        }
    };

    const endpoint = document.getElementById('endpoint');
    const formArea = document.getElementById('form-area');
    const requestPreview = document.getElementById('requestPreview');
    const responsePanel = document.getElementById('responsePanel');
    const tryBtn = document.getElementById('tryBtn');
    const copyCurl = document.getElementById('copyCurl');
    const resetBtn = document.getElementById('resetBtn');

    function renderForm(path) {
        formArea.innerHTML = '';
        const def = mock[path];
        def.schema.forEach(field => {
            const div = document.createElement('div');
            div.className = 'request-field';
            const label = document.createElement('label');
            // show the schema field name, and expose the description as a hover tooltip
            label.textContent = field.name;
            // append red asterisk for required fields
            if (field.required) {
                const requiredSpan = document.createElement('span');
                requiredSpan.textContent = ' *';
                requiredSpan.style.color = '#d32f2f';
                requiredSpan.setAttribute('aria-label', 'required');
                label.appendChild(requiredSpan);
            }
            if (field.description) label.title = field.description;

            // if the field is a currency, render a searchable input + datalist populated from `currencies`
            if (field.name === 'source_currency' || field.name === 'target_currency') {
                const datalistId = `dl-${field.name}`;
                const input = document.createElement('input');
                input.className = 'input';
                input.name = field.name;
                if (field.required) input.setAttribute('required', '');
                input.setAttribute('list', datalistId);
                input.placeholder = field.placeholder || field.description || '';
                input.setAttribute('aria-label', field.description || field.name);

                const dl = document.createElement('datalist');
                dl.id = datalistId;
                // populate options with code and label (label shows friendly text in some browsers)
                Object.keys(currencies).sort().forEach(code => {
                    const opt = document.createElement('option');
                    opt.value = code;
                    const meta = currencies[code] || {};
                    // include a label for richer display where supported
                    opt.label = `${code} — ${meta.name || ''} (${meta.country || ''})`;
                    dl.appendChild(opt);
                });

                // apply default value if provided
                if (field.placeholder) input.value = field.placeholder;

                div.appendChild(label);
                div.appendChild(input);
                div.appendChild(dl);
            } else {
                const input = document.createElement('input');
                input.className = 'input';
                input.name = field.name;
                input.placeholder = field.placeholder || field.description || '';
                // accessibility: associate the input with the label
                if (field.description) input.setAttribute('aria-label', field.description);
                div.appendChild(label);
                div.appendChild(input);
            }
            formArea.appendChild(div);
        });
        updatePreview(path);
    }

    function gatherPayload(path) {
        const def = mock[path];
        if (def.method === 'GET') return null;
        const payload = {};
        def.schema.forEach(f => {
            const el = formArea.querySelector(`[name="${f.name}"]`);
            payload[f.name] = el ? el.value || el.placeholder || '' : '';
        });
        return payload;
    }

    function updatePreview(path) {
        const def = mock[path];
        const payload = gatherPayload(path);
        if (def.method === 'GET') {
            if (path === '/v1/transactions/{id}') {
                const txId = formArea.querySelector('[name="transaction_id"]')?.value || 'tx_987654';
                requestPreview.textContent = `${def.method} /v1/transactions/${txId}`;
            } else {
                requestPreview.textContent = `${def.method} ${path}`;
            }
        } else {
            requestPreview.textContent = `${def.method} ${path}\n\n${JSON.stringify(payload, null, 2)}`;
        }
    }

    function tryIt(path) {
        const def = mock[path];
        if (def.method === 'GET') {
            responsePanel.textContent = JSON.stringify(def.response, null, 2);
            return;
        }
        // emulate using the quote->create flow
        const payload = gatherPayload(path);
        // simple mapping: if quote endpoint return mock.quote_id and include in create step
        if (path === '/v1/transactions/quote') {
            responsePanel.textContent = JSON.stringify(def.response, null, 2);
            // fill quote_id into create form if present on page
            const createQuoteEl = document.querySelector('#form-area [name="quote_id"]');
            if (createQuoteEl) createQuoteEl.value = def.response.quote_id;
        } else if (path === '/v1/transactions/create') {
            // show transaction mock; echo payload
            const resp = Object.assign({}, def.response, { requested: payload });
            responsePanel.textContent = JSON.stringify(resp, null, 2);
        }
    }

    function generateCurl(path) {
        const def = mock[path];
        if (def.method === 'GET') {
            if (path === '/v1/transactions/{id}') {
                const txId = formArea.querySelector('[name="transaction_id"]')?.value || 'tx_987654';
                return `curl https://example.com/v1/transactions/${txId}`;
            }
            return `curl https://example.com${path}`;
        }
        const payload = gatherPayload(path) || {};
        return `curl -X ${def.method} https://example.com${path} -H 'Content-Type: application/json' -d '${JSON.stringify(payload)}'`;
    }

    endpoint.addEventListener('change', () => {
        renderForm(endpoint.value);
    });

    formArea.addEventListener('input', () => {
        updatePreview(endpoint.value);
    });

    tryBtn.addEventListener('click', () => {
        tryIt(endpoint.value);
    });

    copyCurl.addEventListener('click', () => {
        const curl = generateCurl(endpoint.value);
        navigator.clipboard.writeText(curl).then(() => {
            copyCurl.textContent = 'Copied';
            setTimeout(() => copyCurl.textContent = 'Copy curl', 1200);
        });
    });

    resetBtn.addEventListener('click', () => {
        renderForm(endpoint.value);
        responsePanel.textContent = '--';
        requestPreview.textContent = '--';
    });

    // initial
    renderForm(endpoint.value);
})();