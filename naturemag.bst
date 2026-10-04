%% naturemag.bst — minimal Nature/Scientific Reports bibliography style
%% Produces numbered references: Author. Title. Journal Vol, Pages (Year).
%% For full fidelity, use the official Springer Nature .bst from the template.

ENTRY
  { author title journal volume number pages year
    doi url howpublished booktitle publisher series
    note editor edition }
  {}
  { label }

INTEGERS { output.state before.all mid.sentence after.sentence }

FUNCTION {init.state.consts}
{ #0 'before.all :=
  #1 'mid.sentence :=
  #2 'after.sentence :=
}

STRINGS { s t }

FUNCTION {output.nonnull}
{ 's :=
  output.state mid.sentence =
    { ", " * write$ }
    { output.state after.sentence =
        { ". " * write$ }
        { write$ }
      if$
    }
  if$
  mid.sentence 'output.state :=
  s
}

FUNCTION {output}
{ duplicate$ empty$
    'pop$
    'output.nonnull
  if$
}

FUNCTION {output.check}
{ 't :=
  duplicate$ empty$
    { pop$ }
    'output.nonnull
  if$
}

FUNCTION {fin.entry}
{ "." * write$
  newline$
}

FUNCTION {new.block}
{ after.sentence 'output.state := }

FUNCTION {begin.entry}
{ before.all 'output.state := }

FUNCTION {format.authors}
{ author empty$
    { "" }
    { author }
  if$
}

FUNCTION {format.title}
{ title empty$
    { "" }
    { title }
  if$
}

FUNCTION {format.journal}
{ journal empty$
    { "" }
    { "\textit{" journal * "}" * }
  if$
}

FUNCTION {format.volume}
{ volume empty$
    { "" }
    { "\textbf{" volume * "}" * }
  if$
}

FUNCTION {format.pages}
{ pages empty$
    { "" }
    { pages }
  if$
}

FUNCTION {format.year}
{ year empty$
    { "" }
    { "(" year * ")" * }
  if$
}

FUNCTION {format.doi}
{ doi empty$
    { "" }
    { "" }
  if$
}

FUNCTION {article}
{ begin.entry
  format.authors output
  new.block
  format.title output
  new.block
  format.journal output
  format.volume output
  format.pages output
  format.year output
  format.doi output
  fin.entry
}

FUNCTION {inproceedings}
{ begin.entry
  format.authors output
  new.block
  format.title output
  new.block
  booktitle empty$
    { "" }
    { "In " booktitle * }
  if$ output
  format.year output
  fin.entry
}

FUNCTION {incollection}
{ begin.entry
  format.authors output
  new.block
  format.title output
  new.block
  booktitle empty$
    { "" }
    { "In " booktitle * }
  if$ output
  publisher empty$
    { "" }
    { publisher }
  if$ output
  format.year output
  fin.entry
}

FUNCTION {book}
{ begin.entry
  format.authors output
  new.block
  format.title output
  new.block
  publisher empty$
    { "" }
    { publisher }
  if$ output
  format.year output
  fin.entry
}

FUNCTION {misc}
{ begin.entry
  format.authors output
  new.block
  format.title output
  new.block
  howpublished empty$
    { "" }
    { howpublished }
  if$ output
  format.year output
  fin.entry
}

FUNCTION {default.type} { article }

READ

FUNCTION {sortify}
{ purify$
  "l" change.case$
}

FUNCTION {presort}
{ cite$ 'label :=
  label sortify 'sort.key$ :=
}

ITERATE {presort}
SORT

FUNCTION {begin.bib}
{ preamble$ empty$
    'skip$
    { preamble$ write$ newline$ }
  if$
  "\begin{thebibliography}{99}" write$ newline$
}

FUNCTION {end.bib}
{ newline$
  "\end{thebibliography}" write$ newline$
}

FUNCTION {call.type$}
{ type$ empty$
    { "article" }
    { type$ }
  if$
  duplicate$ "article" =
    { pop$ article }
    { duplicate$ "inproceedings" =
        { pop$ inproceedings }
        { duplicate$ "incollection" =
            { pop$ incollection }
            { duplicate$ "book" =
                { pop$ book }
                { pop$ misc }
              if$
            }
          if$
        }
      if$
    }
  if$
}

EXECUTE {begin.bib}
EXECUTE {init.state.consts}

ITERATE { call.type$ }

EXECUTE {end.bib}
