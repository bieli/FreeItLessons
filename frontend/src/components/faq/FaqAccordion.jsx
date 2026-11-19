import { useState } from 'react';
import Collapse from '../layout/Collapse';

/** Questions and answers - one answer open at a time (answers are admin authored HTML). */
export default function FaqAccordion({ faqs = [] }) {
  const [openIndex, setOpenIndex] = useState(null);

  return (
    <dl>
      {faqs.map((faq, index) => {
        const open = openIndex === index;
        return [
          <dt key={`q${faq.id}`} onClick={() => setOpenIndex(open ? null : index)} aria-expanded={open}>
            <h3 className="list-group-item">
              <i className={`glyphicon glyphiconRight ${open ? 'glyphicon-chevron-down' : 'glyphicon-chevron-right'}`} />
              {' '}{faq.question} ?
              <span className="glyphicon glyphicon-plus pull-right" />
            </h3>
          </dt>,
          <Collapse as="dd" key={`a${faq.id}`} open={open}>
            <p className="list-group-item-paragraph">
              <span dangerouslySetInnerHTML={{ __html: faq.answer }} />.
            </p>
          </Collapse>,
        ];
      })}
    </dl>
  );
}
