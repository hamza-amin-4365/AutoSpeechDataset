# AutoSpeechDataset

This tool will solve a major problem for generating speech datasets using youtube videos. Just input your link of video and get a tts/asr ready data in suitable format. Perfect for training speech models.


## Legal & Ethical Note

This tool is stricktly for education purpose only as YouTube cannot be redistributed freely in most cases.  


## High Level Architecture
```mermaid
flowchart TD
    %% --- Custom Styling Definitions ---
    %% Light blue for inputs
    classDef input fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,rx:5,ry:5,color:#000;
    %% Orange for active agents
    classDef agent fill:#fff3e0,stroke:#ef6c00,stroke-width:2px,rx:15,ry:15,color:#000;
    %% Green for database storage
    classDef db fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    %% Hide subgraph borders for cleaner look
    style Row1 fill:none,stroke:none
    style Row2 fill:none,stroke:none
    style Row3 fill:none,stroke:none


    %% --- ROW 1: Flow goes Left to Right --->
    subgraph Row1
        direction LR
        A[YouTube URL Input]:::input --> B[Audio Intake Agent]:::agent --> C[Language Detection Agent]:::agent
    end

    %% --- ROW 2: Parallel Processing (The Bend) ---
    subgraph Row2
        %% These sit below Row 1
        D["ASR Agent (EN)"]:::agent
        E["ASR Agent (UR)"]:::agent
    end

    %% --- ROW 3: Flow goes Right to Left <---
    subgraph Row3
        direction RL
        %% Note the reversed arrows for RL direction
        H[Dataset Builder Agent]:::agent --> G[Quality Control Agent]:::agent --> F[Segmentation Agent]:::agent
    end

    %% Final Output Node sits at the bottom
    I[(Speech Dataset DB)]:::db


    %% --- Connecting the Rows together ---
    %% Connect Row 1 down to Row 2
    C -- English --> D
    C -- Urdu --> E

    %% Connect Row 2 down to Row 3 (Merging back to F)
    D --> F
    E --> F

    %% Connect Row 3 down to Final Output
    H --> I
```
