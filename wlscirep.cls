%% wlscirep.cls  –  Springer Nature / Scientific Reports LaTeX class
%% Minimal reproduction for local compilation; upload to Overleaf for
%% the official template at https://www.overleaf.com/latex/templates/
%% The official class is maintained by Overleaf / Springer Nature.
%%
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{wlscirep}[2024/01/01 Scientific Reports article class]

% ---- options ----
\DeclareOption{fleqn}{\PassOptionsToClass{fleqn}{article}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass{article}

% ---- required packages ----
\RequirePackage[margin=2.5cm]{geometry}
\RequirePackage{graphicx}
\RequirePackage{hyperref}
\RequirePackage[numbers,sort&compress]{natbib}
\RequirePackage{amsmath,amssymb}
\RequirePackage{xcolor}
\RequirePackage{authblk}
\RequirePackage{abstract}
\RequirePackage{titlesec}
\RequirePackage{fancyhdr}
\RequirePackage{caption}
\RequirePackage{lineno}

% ---- fonts ----
\RequirePackage{helvet}
\renewcommand{\familydefault}{\sfdefault}

% ---- keywords command (store for output after maketitle) ----
\newcommand{\@keywords}{}
\newcommand{\keywords}[1]{\renewcommand{\@keywords}{#1}}

% ---- abstract storage (allow \begin{abstract} before \begin{document}) ----
\long\def\@abstracttext{}
\renewenvironment{abstract}{%
  \long\global\def\@abstracttext\bgroup\aftergroup\@abstractfin
}{%
}
\def\@abstractfin#1{%
  \long\gdef\@abstracttext{#1}%
}
% Simpler approach: use collect body
\let\@origabstract\abstract
\let\@endorigabstract\endabstract
\long\gdef\@storedabstract{}
\RenewDocumentEnvironment{abstract}{+b}{%
  \long\gdef\@storedabstract{#1}%
}{}

% ---- title formatting ----
\renewcommand{\maketitle}{%
  \begin{center}
    {\LARGE\bfseries\@title\par}
    \vskip 1em
    {\large\@author\par}
    \vskip 0.5em
  \end{center}
  \ifx\@storedabstract\empty\else
    \vskip 0.5em
    \begin{quote}
    \small\textbf{Abstract}\par\vskip 4pt
    \@storedabstract
    \end{quote}
  \fi
  \ifx\@keywords\empty\else
    \vskip 0.3em
    \noindent\textbf{Keywords:} \@keywords\par
  \fi
  \vskip 1.5em
}

% ---- section formatting ----
\titleformat{\section}{\large\bfseries}{}{0pt}{}
\titleformat{\subsection}{\normalsize\bfseries}{}{0pt}{}
\titleformat{\subsubsection}{\normalsize\itshape}{}{0pt}{}

% ---- headers / footers ----
\pagestyle{fancy}
\fancyhf{}
\fancyhead[R]{\small\thepage}
\renewcommand{\headrulewidth}{0pt}

% ---- caption formatting ----
\captionsetup{font=small, labelfont=bf, labelsep=period}

% ---- bibliography style ----
\bibliographystyle{unsrtnat}

\endinput
