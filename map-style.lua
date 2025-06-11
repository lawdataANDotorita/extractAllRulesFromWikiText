-- Pandoc filter to map HTML classes to Word custom styles
-- Maps law-number, law-number1, law-number2, and law-desc classes to corresponding Word styles

function Div(elem)
  -- Check if the element has classes
  if elem.classes then
    for _, class in ipairs(elem.classes) do
      -- Map specific HTML classes to Word custom styles
      if class == "law-number" or 
         class == "law-number1" or 
         class == "law-number2" or 
         class == "law-number3" or 
         class == "law-desc" then
        -- Set the custom-style attribute for Word
        elem.attributes["custom-style"] = class
        break
      end
    end
  end
  return elem
end

function Link(elem)
    -- Check if the element has classes
    if elem.classes then
      for _, class in ipairs(elem.classes) do
        -- Map specific HTML classes to Word custom styles
        if class == "law-number" or 
           class == "law-number1" or 
           class == "law-number2" or 
           class == "law-number3" or 
           class == "law-number-link" or 
           class == "law-desc" then
          -- Set the custom-style attribute for Word
          elem.attributes["custom-style"] = class
          break
        end
      end
    end
    return elem
  end
  
  function Span(elem)
    -- Check if the element has classes
    if elem.classes then
      for _, class in ipairs(elem.classes) do
        -- Map specific HTML classes to Word custom styles
        if class == "law-number" or 
           class == "law-number1" or 
           class == "law-number2" or 
           class == "law-number3" or 
           class == "law-number-link" or 
           class == "law-desc" then
          -- Set the custom-style attribute for Word
          elem.attributes["custom-style"] = class
          break
        end
      end
    end
    return elem
  end
  