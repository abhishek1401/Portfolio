import { LabeledInput, LabeledTextarea, RemoveButton } from "../../components/FormFields";
import type { EditableItem } from "../../types/dashboard";

interface CollectionEditorProps<T extends EditableItem> {
  title: string;
  items: T[];
  blankItem: T;
  fields: Array<keyof T & string>;
  multiline?: Array<keyof T & string>;
  onChange: (items: T[]) => void;
}

export function CollectionEditor<T extends EditableItem>({
  title,
  items,
  blankItem,
  fields,
  multiline = [],
  onChange,
}: CollectionEditorProps<T>) {
  function updateItem(index: number, field: keyof T & string, value: string) {
    onChange(items.map((item, itemIndex) => (itemIndex === index ? ({ ...item, [field]: value } as T) : item)));
  }

  return (
    <section className="form-section">
      <div className="section-heading">
        <h2>{title}</h2>
        <button type="button" className="secondary" onClick={() => onChange([...items, { ...blankItem }])}>
          Add
        </button>
      </div>

      {items.map((item, index) => (
        <div className="edit-card" key={`${title}-${index}`}>
          <div className="edit-card-header">
            <strong>
              {title.slice(0, -1)} {index + 1}
            </strong>
            <RemoveButton onClick={() => onChange(items.filter((_, itemIndex) => itemIndex !== index))} />
          </div>

          {fields.map((field) => {
            const label = field.charAt(0).toUpperCase() + field.slice(1);
            const value = String(item[field] || "");
            return multiline.includes(field) ? (
              <LabeledTextarea key={field} label={label} value={value} onChange={(next) => updateItem(index, field, next)} />
            ) : (
              <LabeledInput key={field} label={label} value={value} onChange={(next) => updateItem(index, field, next)} />
            );
          })}
        </div>
      ))}
    </section>
  );
}
