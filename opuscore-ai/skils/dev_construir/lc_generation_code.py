# =============================================================================
# lc_CapGenCode_v2.py
# -----------------------------------------------------------------------------
# Capgemini SAP AI Code Generator - v2
# -----------------------------------------------------------------------------
# Purpose : Reads a functional SAP requirement from the "input" folder,
#           identifies the development type, and generates all SAP/BTP
#           artifacts (ABAP, RAP CDS, CAP, Enhancements, Forms, Event Mesh)
#           with Capgemini headers, naming conventions and best practices.
# Author  : Capgemini SAP AI - Code Generation Engine
# Model   : us.anthropic.claude-sonnet-4-20250514-v1:0
# RAG     : WORKSPACE_ID (Workbook ABAP_Move2S4_Final.docx conventions)
# =============================================================================

from dotenv import load_dotenv
import os
import uuid
import glob
import re
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

# ------------------------------------------------------------------------------
# Load environment variables
# ------------------------------------------------------------------------------
load_dotenv()

LLM_API_KEY  = os.getenv("LLM_API_KEY")
WORKSPACE_ID = os.getenv("WORKSPACE_ID")

if not LLM_API_KEY or not WORKSPACE_ID:
    raise EnvironmentError("LLM_API_KEY and WORKSPACE_ID must be defined in .env file")


# ------------------------------------------------------------------------------
# Folders
# ------------------------------------------------------------------------------
INPUT_FOLDER  = os.path.join(os.getcwd(), "input")
OUTPUT_FOLDER = os.path.join(os.getcwd(), "output")


# ------------------------------------------------------------------------------
# Comment styles per SAP object type / file extension
# ------------------------------------------------------------------------------
COMMENT_STYLES = {
    # CDS / RAP / DDL
    'asddls': '--',
    'ddls':   '--',
    'srvd':   '--',
    'bdef':   '--',
    'cdsext': '--',
    'ddlx':   '--',

    # CAP (CDS)
    'cds':    '//',

    # ABAP Classic / OO
    'abap':   '"',
    'prog':   '"',
    'reps':   '"',
    'clas':   '"',
    'intf':   '"',
    'fugr':   '"',
    'func':   '"',
    'msag':   '"',

    # Default
    'txt':    '"',
    'js':     '//',
    'json':   '//',
    'xml':    '<!--',
}

# ------------------------------------------------------------------------------
# File type labels per extension
# ------------------------------------------------------------------------------
FILE_TYPE_MAP = {
    'asddls': 'CDS View Entity (RAP)',
    'ddls':   'DDL Source',
    'srvd':   'Service Definition',
    'bdef':   'Behavior Definition',
    'cdsext': 'CDS View Extension',
    'ddlx':   'CDS Metadata Extension',
    'cds':    'CAP CDS',
    'abap':   'ABAP Program',
    'prog':   'ABAP Program',
    'reps':   'ABAP Report',
    'clas':   'ABAP Class',
    'intf':   'ABAP Interface',
    'fugr':   'Function Group',
    'func':   'Function Module',
    'msag':   'Message Class',
    'txt':    'ABAP',
    'js':     'JavaScript (Fiori/UI5)',
    'json':   'JSON (CAP/Fiori)',
    'xml':    'XML (Fiori/UI5)',
}

# ------------------------------------------------------------------------------
# Development types (detected from input requirement)
# ------------------------------------------------------------------------------
DEV_TYPES = {
    "rap":          "Fiori RAP (Restful ABAP Programming Model)",
    "cap":          "SAP CAP (Cloud Application Programming Model - BTP)",
    "abap":         "Classic ABAP Program / Report",
    "enhancement":  "ABAP Enhancement (EXIT / BAdI / Enhancement Spot)",
    "badi":         "BAdI Implementation",
    "class":        "ABAP OO Class",
    "function":     "ABAP Function Module",
    "form":         "SAP SmartForm / Adobe Form",
    "event_mesh":   "SAP Event Mesh (Inbound / Outbound RAP)",
    "ewm":          "SAP EWM RF Framework",
    "bopf":         "BOPF (Business Object Processing Framework)",
}


# =============================================================================
# LLM Client Factory
# =============================================================================
def create_llm(session_id: str) -> ChatOpenAI:
    """Creates a ChatOpenAI instance bound to a specific session."""
    return ChatOpenAI(
        model="us.anthropic.claude-sonnet-4-20250514-v1:0",
        base_url="https://openai.generative.engine.capgemini.com/v1",
        api_key=LLM_API_KEY,
        max_tokens=8192,
        default_headers={
            "workspace-id": WORKSPACE_ID,
            "session-id":   session_id,
        }
    )


def new_session_id() -> str:
    return str(uuid.uuid4())


# =============================================================================
# Capgemini Header Generator
# =============================================================================
def create_capgemini_header(
    comment_style: str,
    object_name:   str,
    object_type:   str,
    description:   str,
    dev_type:      str,
    session_id:    str,
) -> str:
    """
    Generates the standard Capgemini SAP object header.
    Convention source: Workbook ABAP_Move2S4_Final.docx
    """
    date      = datetime.now().strftime("%d-%m-%Y")
    sep_long  = "-" * 132
    sep_short = "-" * 100

    return (
        f"{comment_style}{sep_long}\n"
        f"{comment_style}{'Capgemini SAP AI Code Generator':^132}\n"
        f"{comment_style}{sep_long}\n"
        f"{comment_style} Object Name    : {object_name}\n"
        f"{comment_style} Object Type    : {object_type}\n"
        f"{comment_style} Description    : {description}\n"
        f"{comment_style} Dev Type       : {dev_type}\n"
        f"{comment_style}{sep_short}\n"
        f"{comment_style} Created By     : Capgemini SAP AI - Code Generation Engine\n"
        f"{comment_style} Created On     : {date}\n"
        f"{comment_style} Workspace-ID   : {WORKSPACE_ID}\n"
        f"{comment_style} Session-ID     : {session_id}\n"
        f"{comment_style} Model          : us.anthropic.claude-sonnet-4-20250514-v1:0\n"
        f"{comment_style} Convention     : Workbook ABAP_Move2S4_Final.docx\n"
        f"{comment_style}{sep_short}\n"
        f"{comment_style} Change History :\n"
        f"{comment_style}   {date} | Capgemini SAP AI | Initial Generation\n"
        f"{comment_style}{sep_long}\n\n"
    )


# =============================================================================
# Prompt Builder — Master Code Generation
# =============================================================================
def build_code_generation_prompt(
    requirement_text: str,
    dev_type_key:     str,
) -> str:
    """
    Builds the master LLM prompt for SAP code generation.
    Incorporates RAG workspace, naming conventions, best practices,
    security rules and all generation rules per development type.
    """

    dev_type_label = DEV_TYPES.get(dev_type_key, "SAP Development")
    date           = datetime.now().strftime("%d-%m-%Y")

    # ------------------------------------------------------------------
    # Type-specific generation instructions
    # ------------------------------------------------------------------
    type_instructions = _build_type_instructions(dev_type_key)

    return f"""
You are a Senior SAP Developer expert in:
  - ABAP (Classic, OO, Clean Core, S/4HANA)
  - Fiori RAP (Restful ABAP Programming Model)
  - SAP CAP (Cloud Application Programming Model - BTP)
  - ABAP Enhancements: User Exits, BAdIs, Enhancement Spots
  - ABAP Classes, Function Modules, SmartForms, Adobe Forms
  - SAP EWM RF Framework
  - BOPF (Business Object Processing Framework)
  - SAP Event Mesh (Inbound / Outbound)

================================================================================
KNOWLEDGE BASE RULES
================================================================================
1. FIRST: use the RAG knowledge base from WORKSPACE_ID "{WORKSPACE_ID}" as
   the primary source for best practices, naming conventions and templates.
2. Use the document "Workbook ABAP_Move2S4_Final.docx" for:
   - Object naming conventions (prefix Z + functional abbreviation)
   - Capgemini header format
   - S/4HANA readiness rules
3. If the RAG does not contain specific information, use your LLM training
   knowledge and SAP official documentation best practices.

================================================================================
DEVELOPMENT TYPE REQUESTED
================================================================================
Type  : {dev_type_label}
Date  : {date}

================================================================================
FUNCTIONAL REQUIREMENT
================================================================================
{requirement_text}

================================================================================
GENERAL MANDATORY RULES
================================================================================
1.  NAMING CONVENTION  : All objects must be prefixed with Z followed by a
    functional abbreviation per "Workbook ABAP_Move2S4_Final.docx".
    Examples:
      - ABAP Program   → ZPRG_<FUNCTIONAL_NAME>
      - CDS View       → ZI_<ENTITY_NAME> (interface), ZC_<ENTITY_NAME> (consumption)
      - Behavior Def   → ZI_<ENTITY_NAME> / ZC_<ENTITY_NAME>
      - Service Def    → ZUI_<SERVICE_NAME>_O4 (OData v4)
      - Class          → ZCL_<FUNCTIONAL_NAME>
      - Interface      → ZIF_<FUNCTIONAL_NAME>
      - Function Group → ZFG_<FUNCTIONAL_NAME>
      - Function Module→ Z_<FUNCTIONAL_NAME>
      - BAdI Impl      → ZCL_BADI_<FUNCTIONAL_NAME>
      - Enhancement    → ZENH_<FUNCTIONAL_NAME>
      - CAP Service    → z-<functional-name> (kebab-case)
      - CAP Entity     → Z<EntityName>

2.  CAPGEMINI HEADER   : Every generated file MUST start with the standard
    Capgemini header as defined in "Workbook ABAP_Move2S4_Final.docx":
    -----------------------------------------------------------------------
    " Created By     : Capgemini SAP AI - Code Generation Engine
    " Created On     : {date}
    " Convention     : Workbook ABAP_Move2S4_Final.docx
    -----------------------------------------------------------------------
    Adapt the comment character per language (", --, //)

3.  DOCUMENTATION      : Inline comments are mandatory. Every method, class,
    CDS entity and important logic block must have a brief comment.
    Be concise but clear.

4.  BEST PRACTICES     : Apply SAP and Capgemini best practices:
    - ABAP  : Use NEW, VALUE, CORRESPONDING, avoid obsolete statements
              (MOVE, COMPUTE, WRITE TO, SELECT *).
    - CDS   : Use @AbapCatalog.viewEnhancementCategory, proper annotations.
    - RAP   : Use managed scenario unless unmanaged is explicitly required.
    - CAP   : Use @requires, proper srv/ structure, handlers in .js or .ts.
    - Clean Core : Avoid modifications to standard SAP objects. Use BAdIs.

5.  SECURITY           : Always include:
    - ABAP programs   : AUTHORITY-CHECK OBJECT '...' ID '...' DUMMY.
    - RAP / CDS       : @AccessControl.authorizationCheck: #CHECK
                        Generate a DCL (Access Control) object granting
                        Company Code BR01 as minimum if not specified.
    - CAP             : @requires: 'authenticated-user' minimum.
    - BAdIs / Exits   : Authority check at entry point.
    - If requirement specifies authorizations, use them; otherwise default
      to Company Code BR01.

6.  ERROR HANDLING     : Use structured TRY/CATCH with cx_root or specific
    exception classes. Never ignore exceptions silently.

7.  OUTPUT FORMAT      : For EACH generated file output:
    a) A line with: === FILE: <filename>.<extension> ===
    b) The complete source code of that file (with Capgemini header)
    c) A line with: === END FILE: <filename>.<extension> ===
    Generate ALL files needed for the requirement (CDS, BDEF, SRVD, class,
    etc.) — do NOT skip any artifact.

8.  COMPLETENESS       : Generate 100% complete, compilable code.
    Do NOT use placeholders like "// TODO" or "... rest of code ...".
    Every method must have a full implementation.

================================================================================
TYPE-SPECIFIC INSTRUCTIONS
================================================================================
{type_instructions}

================================================================================
OUTPUT
================================================================================
Return ONLY the generated source code files using the === FILE / === END FILE
delimiters. Do NOT add any explanation before or after the files.
Do NOT add a summary section — the code is self-documented via comments.
"""


def _build_type_instructions(dev_type_key: str) -> str:
    """Returns the generation instructions specific to each development type."""

    instructions = {

        # ------------------------------------------------------------------
        "rap": """
FIORI RAP GENERATION RULES:
  1.  Generate the FULL RAP stack:
        a) Interface CDS View        : ZI_<Name>.asddls
        b) Consumption CDS View      : ZC_<Name>.asddls
        c) Metadata Extension (UI)   : ZC_<Name>.ddlx
        d) Behavior Definition       : ZI_<Name>.bdef (abstract / managed)
        e) Behavior Implementation   : ZCL_BP_<Name>.clas.abap
        f) Service Definition        : ZUI_<Name>_O4.srvd
        g) Access Control (DCL)      : ZI_<Name>.dcl  and  ZC_<Name>.dcl
        h) CDS projection if needed

  2.  Use @OData.publish: true on the Service Definition for automatic
      service binding generation instruction (comment it in the file).

  3.  CDS annotations:
        - @AbapCatalog.viewEnhancementCategory: [#NONE]
        - @AccessControl.authorizationCheck: #CHECK
        - @Metadata.allowExtensions: true
        - @UI annotations on the Metadata Extension (.ddlx)

  4.  Behavior Definition:
        - Use 'managed' scenario with ETag and draft if it is a
          transactional app. Use 'interface' + 'projection' pattern.
        - Define standard CRUD operations + validations + determinations
          as needed by the requirement.
        - Use 'with additional save' when calling BAPIs/Function Modules.

  5.  Behavior Implementation Class (ZCL_BP_<Name>):
        - Implement FOR MODIFY / FOR VALIDATE / FOR DETERMINE methods.
        - BAPI calls go inside 'save_modified' or dedicated action methods.
        - Map RAP messages (mo_reported, mo_failed, mo_mapped) properly.
        - Use cl_abap_tx_exit for BAPI commit control.

  6.  List Report: use @UI.lineItem annotations. Detail page: @UI.fieldGroup.

  7.  If the requirement mentions calling a BAPI (e.g. condition change),
        wrap the BAPI call in a managed action or in save_modified.
        Always check RETURN table for errors and map to RAP messages.
""",

        # ------------------------------------------------------------------
        "cap": """
CAP (CLOUD APPLICATION PROGRAMMING MODEL) GENERATION RULES:
  1.  Generate the full CAP project structure inside output/cap/<ProjectName>/:
        - package.json
        - .cdsrc.json
        - db/schema.cds          (data model)
        - srv/service.cds        (service definition)
        - srv/service-handler.js (Node.js handler OR .ts for TypeScript)
        - app/fiori-annotations.cds (optional UI annotations)
        - mta.yaml               (BTP deployment descriptor)

  2.  Use CDS @requires and @restrict for authorization.
        Minimum: @requires: 'authenticated-user'

  3.  Service handler must implement:
        - CREATE / READ / UPDATE / DELETE handlers as needed.
        - BAPI or RFC calls via node-rfc or @sap-cloud-sdk/connectivity.
        - Proper error propagation using req.error() or throw new Error().

  4.  package.json must include:
        "@sap/cds": "^7", "@sap/cds-dk": "^7",
        "@sap/cloud-sdk-core" (if RFC/BAPI calls needed).

  5.  mta.yaml: include hdi-container, xsuaa, destination service instances.

  6.  All CDS entities: prefix Z (e.g., entity ZConditions { ... }).
        Naming: kebab-case for service file names, PascalCase for entities.
""",

        # ------------------------------------------------------------------
        "abap": """
ABAP PROGRAM / REPORT GENERATION RULES:
  1.  Generate a complete ABAP program (.abap extension).
  2.  Program name: ZPRG_<FUNCTIONAL_NAME> or ZREP_<FUNCTIONAL_NAME>.
  3.  Use REPORT statement with proper message class reference.
  4.  Structure: Selection Screen → Data Declarations → Main Logic →
      Subroutines / Methods (prefer OO with local class lcl_main).
  5.  Use ALV (cl_salv_table or cl_gui_alv_grid) for list output.
  6.  AUTHORITY-CHECK before any data access.
  7.  No SELECT * — always specify field list.
  8.  Use internal tables with TYPE TABLE OF with header-free declarations.
  9.  All database access via CDS Views when available (S/4HANA).
""",

        # ------------------------------------------------------------------
        "enhancement": """
ABAP ENHANCEMENT / EXIT / BAdI GENERATION RULES:
  1.  Identify whether the requirement needs:
        a) User Exit (INCLUDE-based EXIT_*)
        b) BAdI (cl_badi_handler / GET BADI / CALL BADI)
        c) Enhancement Spot (ENHANCEMENT / ENDENHANCEMENT)
  2.  Generate:
        - The BAdI implementation class: ZCL_BADI_<NAME>.clas.abap
        - Enhancement implementation include if applicable.
  3.  BAdI class must implement the correct BAdI interface.
  4.  Always include AUTHORITY-CHECK at the entry of the implementation.
  5.  Comment the SE18 / SE19 activation steps inside the code header.
  6.  Use Clean Core approach: prefer published BAdIs over modifications.
""",

        # ------------------------------------------------------------------
        "badi": """
BAdI IMPLEMENTATION GENERATION RULES:
  1.  Generate ZCL_BADI_<NAME>.clas.abap implementing the BAdI interface.
  2.  Include GET BADI / CALL BADI usage example in a helper snippet.
  3.  Full method implementations — no empty stubs.
  4.  Header must document: BAdI name, Enhancement Spot, Interface name.
  5.  AUTHORITY-CHECK at method entry.
""",

        # ------------------------------------------------------------------
        "class": """
ABAP OO CLASS GENERATION RULES:
  1.  File: ZCL_<NAME>.clas.abap
  2.  Generate CLASS ... DEFINITION and CLASS ... IMPLEMENTATION sections.
  3.  Properly scope attributes (PRIVATE / PROTECTED / PUBLIC).
  4.  Constructor must validate mandatory parameters.
  5.  All public methods must have full ABAP Doc comments /** ... */.
  6.  Use FINAL for classes not meant for inheritance.
  7.  Implement IF_SERIALIZABLE_OBJECT if the class needs serialization.
""",

        # ------------------------------------------------------------------
        "function": """
FUNCTION MODULE GENERATION RULES:
  1.  Generate: ZFG_<NAME>.fugr.abap (function group include)
                Z_<NAME>.func.abap   (function module source)
  2.  Declare all IMPORTING / EXPORTING / TABLES / EXCEPTIONS parameters.
  3.  Full inline documentation in the header.
  4.  AUTHORITY-CHECK at entry.
  5.  Use RAISE for exception propagation.
  6.  Prefer RFC-enabled function modules when integration is needed.
""",

        # ------------------------------------------------------------------
        "form": """
SAP FORM GENERATION RULES:
  1.  Generate the ABAP driver program: ZPRG_FORM_<NAME>.abap
        - Selects data, calls OPEN_FORM / CALL_FORM / CLOSE_FORM
          (SmartForms) or FP_JOB_OPEN / FP_FUNCTION_MODULE_EXECUTE
          (Adobe Forms).
  2.  Generate a pseudo-code / annotation CDS or text file describing
      the form layout, fields and conditions: ZFORM_<NAME>_LAYOUT.txt
  3.  AUTHORITY-CHECK before form execution.
  4.  Error handling via EXCEPTIONS on CALL FUNCTION.
""",

        # ------------------------------------------------------------------
        "event_mesh": """
SAP EVENT MESH / RAP BUSINESS EVENTS GENERATION RULES:
  1.  OUTBOUND (RAP raises event → Event Mesh → subscriber):
        a) Behavior Definition (.bdef): add 'event <EventName> parameter ...'
        b) Behavior Implementation: RAISE ENTITY EVENT in the action/modify.
        c) Event Binding object description (comment in srvd or bdef).
        d) Generate ZCL_BP_<NAME>.clas.abap with event raising logic.

  2.  INBOUND (Event Mesh → RAP event handler):
        a) Generate ZCL_EVT_HANDLER_<NAME>.clas.abap implementing
           IF_ABAP_BEHV_EVENT_HANDLER.
        b) Register in the Event Consumption Model (comment instructions).
        c) Implement ON EVENT method with proper error handling.

  3.  In both cases generate:
        - The supporting CDS / BDEF artifacts.
        - A README-style comment block explaining the Event Mesh
          topic configuration and channel setup steps.
""",

        # ------------------------------------------------------------------
        "ewm": """
SAP EWM RF FRAMEWORK GENERATION RULES:
  1.  Generate the RF step class: ZCL_EWM_RF_<NAME>.clas.abap
        implementing /SCWM/IF_RF_PROCESS or the relevant EWM interface.
  2.  Generate the screen flow description as inline comments
      (EWM RF uses dynpro-based screens via /SCWM/RF_SCREEN).
  3.  Implement: VERIFY, PROCESS, CLOSE methods.
  4.  Use /SCWM/ APIs for warehouse tasks and stock changes.
  5.  AUTHORITY-CHECK with EWM warehouse number.
  6.  Error messages via /SCWM/CX_RF or message class.
""",

        # ------------------------------------------------------------------
        "bopf": """
BOPF GENERATION RULES:
  1.  Generate the BOPF node class: ZCL_BOPF_<NAME>.clas.abap
        implementing /BOBF/IF_FRW_ACTION or /BOBF/IF_FRW_DETERMINATION
        as required.
  2.  Generate a helper description file listing:
        - Business Object name
        - Node hierarchy
        - Actions / Determinations / Validations to be configured in BOBX.
  3.  Full implementation of EXECUTE or EXECUTE_FOR_QUERY methods.
  4.  Map results to CT_DATA table parameter.
  5.  AUTHORITY-CHECK at entry.
""",
    }

    return instructions.get(dev_type_key, """
GENERAL SAP DEVELOPMENT RULES:
  - Follow SAP and Capgemini best practices.
  - Apply naming conventions from Workbook ABAP_Move2S4_Final.docx.
  - Generate complete, compilable code with Capgemini header.
  - Include AUTHORITY-CHECK and structured error handling.
""")


# =============================================================================
# Continuation Prompt
# =============================================================================
def build_continuation_prompt() -> str:
    return (
        "Your previous response was truncated due to token limits.\n"
        "MANDATORY RULES FOR CONTINUATION:\n"
        "  1. Resume EXACTLY where the previous response was cut off.\n"
        "  2. Do NOT repeat any code already output.\n"
        "  3. Do NOT add preamble, explanation or headers.\n"
        "  4. Continue outputting ONLY the remaining source code.\n"
        "  5. Maintain === FILE / === END FILE delimiters for remaining files.\n"
        "  6. Complete ALL remaining files until the very end.\n"
        "Continue now:"
    )


# =============================================================================
# LLM Invocation with Continuation Loop
# =============================================================================
def _extract_finish_reason(response) -> str:
    try:
        metadata      = getattr(response, "response_metadata", {}) or {}
        finish_reason = metadata.get("finish_reason", "")
        if finish_reason:
            return finish_reason.lower()
        additional    = getattr(response, "additional_kwargs", {}) or {}
        return additional.get("finish_reason", "stop").lower()
    except Exception:
        return "stop"


def invoke_llm_with_continuation(
    llm:            ChatOpenAI,
    initial_prompt: str,
    max_iterations: int = 20,
) -> str:
    """
    Invokes the LLM, handling truncated responses via continuation loop.
    Returns the full concatenated generated code as a single string.
    """
    full_parts: list[str] = []
    messages:   list      = [HumanMessage(content=initial_prompt)]
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"  → LLM call #{iteration} (invoking...)")

        response      = llm.invoke(messages)
        chunk         = response.content
        finish_reason = _extract_finish_reason(response)

        print(f"  → LLM call #{iteration} finished | "
              f"finish_reason='{finish_reason}' | chars={len(chunk)}")

        if not chunk:
            print(f"  ⚠ Empty chunk on iteration #{iteration}. Stopping.")
            break

        full_parts.append(chunk)

        if finish_reason == "stop":
            print(f"  ✓ LLM completed (stop) on iteration #{iteration}.")
            break
        elif finish_reason == "length":
            print(f"  ⚠ Truncated (length) on iteration #{iteration}. Continuing...")
            messages.append(AIMessage(content=chunk))
            messages.append(HumanMessage(content=build_continuation_prompt()))
        else:
            print(f"  ⚠ Unexpected finish_reason='{finish_reason}'. Stopping.")
            break
    else:
        print(f"  ⚠ Max iterations ({max_iterations}) reached. Output may be incomplete.")

    return "".join(full_parts).strip()


# =============================================================================
# Output File Parser
# Splits LLM response into individual files using === FILE / === END FILE ===
# =============================================================================
def parse_llm_output_to_files(llm_output: str) -> list[dict]:
    """
    Parses the LLM output and extracts individual files.

    Expected LLM format:
        === FILE: <filename>.<ext> ===
        <source code>
        === END FILE: <filename>.<ext> ===

    Returns a list of dicts: [{"filename": str, "content": str}, ...]
    """
    files     = []
    # Pattern tolerates optional spaces and case variations
    pattern   = re.compile(
        r"===\s*FILE:\s*(.+?)\s*===\s*\n(.*?)\n===\s*END FILE:\s*.+?\s*===",
        re.DOTALL | re.IGNORECASE,
    )

    for match in pattern.finditer(llm_output):
        filename = match.group(1).strip()
        content  = match.group(2).strip()
        files.append({"filename": filename, "content": content})

    if not files:
        # Fallback: if no delimiters found, save entire output as single file
        print("  ⚠ No === FILE === delimiters found. Saving full output as raw file.")
        files.append({"filename": "output_raw.txt", "content": llm_output})

    return files


# =============================================================================
# Development Type Detector
# =============================================================================
def detect_dev_type(requirement_text: str) -> str:
    """
    Detects the primary development type from the requirement text.
    Uses keyword matching. Returns a key from DEV_TYPES.
    """
    text_lower = requirement_text.lower()

    keyword_map = [
        ("event mesh",        "event_mesh"),
        ("event",             "event_mesh"),
        ("outbound event",    "event_mesh"),
        ("inbound event",     "event_mesh"),
        ("ewm",               "ewm"),
        ("rf framework",      "ewm"),
        ("bopf",              "bopf"),
        ("cap ",              "cap"),
        ("cloud application", "cap"),
        ("btp",               "cap"),
        ("node.js",           "cap"),
        ("rap ",              "rap"),
        ("fiori",             "rap"),
        ("odata",             "rap"),
        ("list report",       "rap"),
        ("object page",       "rap"),
        ("cds view",          "rap"),
        ("badi",              "badi"),
        ("bad i",             "badi"),
        ("enhancement",       "enhancement"),
        ("user exit",         "enhancement"),
        ("exit",              "enhancement"),
        ("function module",   "function"),
        ("function group",    "function"),
        ("form",              "form"),
        ("smartform",         "form"),
        ("adobe form",        "form"),
        ("class",             "class"),
        ("report",            "abap"),
        ("abap program",      "abap"),
        ("program",           "abap"),
    ]

    for keyword, dev_key in keyword_map:
        if keyword in text_lower:
            return dev_key

    # Default fallback
    return "abap"


# =============================================================================
# File Writer
# =============================================================================
def write_output_file(
    output_folder:  str,
    filename:       str,
    content:        str,
    comment_style:  str,
    object_name:    str,
    object_type:    str,
    description:    str,
    dev_type:       str,
    session_id:     str,
) -> str:
    """
    Writes a generated source file to the output folder.
    Prepends the Capgemini header if not already present in the content.
    Returns the full output path.
    """
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, filename)

    # Prepend Capgemini header only if the LLM did not already include it
    capgemini_marker = "Capgemini SAP AI"
    if capgemini_marker not in content[:500]:
        header  = create_capgemini_header(
            comment_style=comment_style,
            object_name=object_name,
            object_type=object_type,
            description=description,
            dev_type=dev_type,
            session_id=session_id,
        )
        content = header + content

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return output_path


# =============================================================================
# Get comment style and file type from filename extension
# =============================================================================
def get_comment_style_and_type(filename: str):
    _, ext     = os.path.splitext(filename)
    ext        = ext.lower().lstrip(".")
    comment    = COMMENT_STYLES.get(ext, '"')
    file_type  = FILE_TYPE_MAP.get(ext, "SAP Object")
    return comment, file_type, ext


# =============================================================================
# Core Requirement Processor
# =============================================================================
def process_requirement_file(req_file_path: str, output_folder: str):
    """
    Reads a functional requirement file, detects the development type,
    invokes the LLM to generate code, parses the output and writes all
    generated files to the output folder.
    """
    print(f"\n{'=' * 80}")
    print(f"  Processing requirement: {os.path.basename(req_file_path)}")
    print(f"{'=' * 80}")

    # --- Read requirement ---
    try:
        with open(req_file_path, "r", encoding="utf-8") as f:
            requirement_text = f.read().strip()
    except Exception as e:
        print(f"✗ Error reading requirement file: {e}")
        return

    if not requirement_text:
        print("✗ Requirement file is empty. Skipping.")
        return

    # --- Detect development type ---
    dev_type_key   = detect_dev_type(requirement_text)
    dev_type_label = DEV_TYPES.get(dev_type_key, "SAP Development")
    print(f"  → Detected dev type : {dev_type_label}")

    # --- Create session ---
    session_id = new_session_id()
    print(f"  → Session ID        : {session_id}")

    # --- Create LLM ---
    llm = create_llm(session_id)

    # --- Build prompt ---
    prompt = build_code_generation_prompt(requirement_text, dev_type_key)

    # --- Invoke LLM ---
    try:
        print("  → Invoking LLM (RAG-based code generation)...")
        llm_output = invoke_llm_with_continuation(
            llm=llm,
            initial_prompt=prompt,
            max_iterations=20,
        )

        if not llm_output:
            raise ValueError("LLM returned empty output after all iterations.")

    except Exception as e:
        print(f"✗ LLM error: {e}")
        return

    # --- Parse LLM output into individual files ---
    generated_files = parse_llm_output_to_files(llm_output)
    print(f"  → Files to write    : {len(generated_files)}")

    # --- Determine sub-folder based on dev type ---
    # CAP projects go into their own sub-folder
    if dev_type_key == "cap":
        req_base    = os.path.splitext(os.path.basename(req_file_path))[0]
        file_output = os.path.join(output_folder, "cap", req_base)
    else:
        file_output = output_folder

    # --- Write each generated file ---
    written = 0
    for file_info in generated_files:
        filename       = file_info["filename"]
        content        = file_info["content"]
        comment_style, object_type, ext = get_comment_style_and_type(filename)
        object_name    = os.path.splitext(filename)[0].upper()

        try:
            out_path = write_output_file(
                output_folder=file_output,
                filename=filename,
                content=content,
                comment_style=comment_style,
                object_name=object_name,
                object_type=object_type,
                description=f"Generated from requirement: {os.path.basename(req_file_path)}",
                dev_type=dev_type_label,
                session_id=session_id,
            )
            print(f"  ✓ Written: {out_path}")
            written += 1
        except Exception as e:
            print(f"  ✗ Error writing {filename}: {e}")

    print(f"\n  ✓ {written}/{len(generated_files)} files written to: {file_output}")


# =============================================================================
# Main Execution
# =============================================================================
def main():
    print(f"\n{'=' * 80}")
    print("  Capgemini SAP AI Code Generator - v2")
    print("  Convention: Workbook ABAP_Move2S4_Final.docx")
    print(f"{'=' * 80}")

    # --- Validate folders ---
    if not os.path.exists(INPUT_FOLDER):
        print(f"✗ Input folder not found: {INPUT_FOLDER}")
        print("  Please create the 'input' folder and place requirement files there.")
        return

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # --- Find requirement files ---
    supported_req_formats = [
        "*.txt", "*.md", "*.req", "*.docx_extracted.txt"
    ]

    req_files = []
    for pattern in supported_req_formats:
        req_files.extend(glob.glob(os.path.join(INPUT_FOLDER, pattern)))

    if not req_files:
        print("✗ No requirement files found in the 'input' folder.")
        print("  Supported formats: .txt, .md, .req")
        return

    print(f"  Found {len(req_files)} requirement file(s):")
    for rf in req_files:
        print(f"    - {os.path.basename(rf)}")
    print(f"{'=' * 80}\n")

    # --- Process each requirement ---
    for req_file in req_files:
        process_requirement_file(req_file, OUTPUT_FOLDER)

    print(f"\n{'=' * 80}")
    print(f"✓ Code generation completed for {len(req_files)} requirement(s).")
    print(f"✓ Output folder : {OUTPUT_FOLDER}")
    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    main()