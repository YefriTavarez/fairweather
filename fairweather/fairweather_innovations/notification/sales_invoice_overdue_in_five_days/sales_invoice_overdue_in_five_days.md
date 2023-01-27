<h3>Dear {{ doc.customer_name }},</h3>

{% set today = frappe.utils.nowdate() %}
{% set due_date = frappe.utils.getdate(doc.due_date) %}
{% set days = frappe.utils.date_diff(due_date, today) %}

<p>
    We hope this email finds you well. We are writing to remind you that 
    invoice number #{{ doc.name }} for {{ doc.get_formatted("grand_total") }} 
    is due in {{ days }} days. As of now, we have not received payment for 
    this invoice.
</p>

<p>
    We would greatly appreciate it if you could take the necessary steps to 
    ensure that this invoice is paid in full before the due date. Please let 
    us know if you require any additional information or if there are any 
    issues that need to be addressed.
</p>

<p>
    As a reminder, payment can be made by ACH, Wire Transfer, Check or Credit 
    Card (2.5% CC processing fee). If you have any questions or concerns, 
    please do not hesitate to contact us.
</p>

<p>
    Thank you for your prompt attention to this matter.
</p>

<p>
    Best regards,
</p>
