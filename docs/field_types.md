# Supported Fields
Presidio contains predefined recognizers for PII entities (fields). This page describes the different entities Presidio can detect and the method Presidio employs to detect those.

In addition, Presidio allows you to add custom fields by API or code. For more information, refer to the [custom fields documentation](custom_fields.md).



<h2>Global</h2>
<table>
  <tbody>
    <tr>
      <th>FieldType</th>
      <th>Description</th>
      <th>Detection Method</th>
    </tr>
    <tr>
      <td>
        <code>
          <span>CREDIT_CARD</span>
        </code>
      </td>
      <td>
        <p>A
          <em>credit card number</em> is between 12 to 19 digits. https://en.wikipedia.org/wiki/Payment_card_number</p>
      </td>
      <td>Pattern match and checksum</td>
    </tr>
    <tr>
      <td>
        <code>
          <span>CRYPTO</span>
        </code>
      </td>
      <td>
        <p>A
          <em>Crypto wallet number</em>. Currently only Bitcoin address is supported</p>
      </td>
      <td>Pattern match and checksum</td>
    </tr>
    <tr>
      <td>
        <code>
          <span>DATE_TIME</span>
        </code>
      </td>
      <td>
        <p>Absolute or relative dates or periods or times smaller than a day.</p>
      </td>
      <td>Pattern match and context</td>
    </tr>
    <tr>
      <td>
        <code>
          <span>DOMAIN_NAME</span>
        </code>
      </td>
      <td>
        <p>A
          <em>domain name</em> as defined by the DNS standard.</p>
      </td>
      <td>Pattern match and top level domain validation</td>
    </tr>
    <tr>
      <td>
        <code>
          <span>EMAIL_ADDRESS</span>
        </code>
      </td>
      <td>
        <p>An
          <em>email address</em> identifies an email box to which email messages are delivered</p>
      </td>
      <td>Pattern match and RFC-822 validation</td>
    </tr>
    <tr>
      <td>
        <code>
          <span>IBAN_CODE</span>
        </code>
      </td>
      <td>
        <p>The
          <em>International Bank Account Number (IBAN)</em> is an internationally agreed system of identifying bank accounts across national borders to facilitate the communication and processing of cross border transactions with a reduced risk of transcription errors.</p>
      </td>
      <td>Pattern match and checksum</td>
    </tr>
    <tr>
      <td>
        <code>
          <span>IP_ADDRESS</span>
        </code>
      </td>
      <td>
        <p>An
          <em>Internet Protocol (IP) address</em> (either IPv4 or IPv6).</p>
      </td>
      <td>Pattern match and checksum</td>
    </tr>
    <tr>
      <td>
        <code>
          <span>NRP</span>
        </code>
      </td>
      <td>
        <p>A person’s
          <em>Nationality, religious or political group</em>.</p>
      </td>
      <td>Word and phrase list</td>
    </tr>
    <tr>
      <td>
        <code>
          <span>LOCATION</span>
        </code>
      </td>
      <td>
        <p>Name of politically or geographically defined location (cities, provinces, countries, international regions, bodies of water, mountains</p>
      </td>
      <td>Custom logic and context</td>
    </tr>
    <tr>
      <td>
        <code>
          <span>PERSON</span>
        </code>
      </td>
      <td>
        <p>A full
          <em>person name</em>, which can include first names, middle names or initials, and last names.</p>
      </td>
      <td>Custom logic and context</td>
    </tr>
    <tr>
      <td>
        <code>
          <span>PHONE_NUMBER</span>
        </code>
      </td>
      <td>
        <p>A
          <em>telephone number</em>
        </p>
      </td>
      <td>Custom logic, pattern match and context</td>
    </tr>
  </tbody>
</table>
<h2>USA</h2>
<table>
  <tbody>
    <tr>
      <th>FieldType</th>
      <th>Description</th>
      <th>Detection Method</th>
    </tr>
    <tr>
      <td>
        <code>
          <span>US_BANK_NUMBER</span>
        </code>
      </td>
      <td>
        <p>A
          <em>US bank account number</em> is between 8 to 17 digits.</p>
      </td>
      <td>Pattern match and context</td>
    </tr>
    <tr>
      <td>
        <code>
          <span>US_DRIVER_LICENSE</span>
        </code>
      </td>
      <td>
        <p>A
          <em>US driver license</em>.  according to https://ntsi.com/drivers-license-format/</p>
      </td>
      <td>Pattern match and context</td>
    </tr>
    <tr>
      <td>
        <code>
          <span>US_ITIN</span>
        </code>
      </td>
      <td>
        <p><em>US Individual Taxpayer Identification Number (ITIN).</em> Nine digits that start with a "9" and contain a "7" or "8" as the 4 digit.</p>
      </td>
      <td>Pattern match and context</td>
    </tr>
    <tr>
      <td>
        <code>
          <span>US_PASSPORT</span>
        </code>
      </td>
      <td>
        <p>A
          <em>US passport number</em> with 9 digits.</p>
      </td>
      <td>Pattern match and context</td>
    </tr>
    <tr>
      <td>
        <code>
          <span>US_SSN</span>
        </code>
      </td>
      <td>
        <p>An
          <em>US Social Security Number (SSN)</em> with 9 digits.
          </p>
      </td>
      <td>Pattern match and context</td>
    </tr>
  </tbody>
</table>
<h2>UK</h2>
<table>
  <tbody>
    <tr>
      <th>FieldType</th>
      <th>Description</th>
      <th>Detection Method</th>
    </tr>
    <tr>
      <td>
        <code>
          <span>UK_NHS</span>
        </code>
      </td>
      <td>
        <p>A
          <em>UK NHS number</em> is 10 digits.</p>
      </td>
      <td>Pattern match and checksum</td>
    </tr>
  </tbody>
</table>
<hr/>
<h2>All fields</h2>
In case you need Presidio to return all possible PII entities, in your Presidio deployment, you need to set the `allFields` flag to `true`.

For example:
```json
"analyzeTemplate":{"allFields":true}
```
<hr/>
<h2>Custom fields</h2>
Presidio supports custom fields. Refer to the <a href="custom_fields.md">custom fields documentation</a> to learn more.
<hr/>