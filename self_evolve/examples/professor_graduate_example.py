"""
Example usage of Professor + Graduate Self-Evolve System
Updated for OpenAI Responses API with enhanced tool use
"""

import os
import json
from datetime import datetime
from ..config import FrameworkConfig, ModelConfig, WorkerConfig
from ..models import ProfessorModel
from ..utils import setup_logging


def save_session_to_markdown(results, output_path_base, session_dir=None):
    """Save session results to organized markdown files with structured directory layout"""
    
    # Use provided session directory or extract from output path
    if session_dir is None:
        session_dir = os.path.dirname(output_path_base)
    
    # Create organized directory structure
    os.makedirs(session_dir, exist_ok=True)
    os.makedirs(os.path.join(session_dir, "professor_iterations"), exist_ok=True)
    
    # Main index file path
    index_path = os.path.join(session_dir, "README.md")
    
    try:
        # 1. Create main index file (README.md)
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("# Self-Evolve Agents Session Report\n\n")
            f.write(f"**Session ID**: {os.path.basename(session_dir)}\n")
            f.write(f"**Timestamp**: {results['timestamp']}\n")
            f.write(f"**API Version**: {results['api_version']}\n")
            f.write(f"**Total Execution Time**: {results['execution_time_seconds']:.2f} seconds\n\n")
            
            # System Configuration
            f.write("## System Architecture\n\n")
            f.write("This session implements the **Self-Evolve Agents (SE-Agents)** framework with:\n")
            f.write("- **Hierarchical Agent Organization**: Professor as coordinator with dynamic Worker generation\n")
            f.write("- **Self-Evolve Mechanism**: Triple-QA structure for iterative refinement\n")
            f.write("- **Nested Self-Evolution**: Applied at both Professor and Worker levels\n\n")
            
            f.write("## Configuration\n\n")
            config = results.get('system_config', {})
            f.write(f"- **Professor Model**: {config.get('professor_model', 'N/A')}\n")
            f.write(f"- **Evaluator Model**: {config.get('evaluator_model', 'N/A')}\n")
            f.write(f"- **Refiner Model**: {config.get('refiner_model', 'N/A')}\n")
            f.write(f"- **Worker Model**: {config.get('worker_model', 'N/A')}\n")
            f.write(f"- **Worker Max Self-Evolve Iterations**: {config.get('worker_max_self_evolve_iterations', 'N/A')}\n")
            f.write(f"- **Reasoning Effort**: {config.get('reasoning_effort', 'N/A')}\n")
            f.write(f"- **Code Interpreter**: {config.get('enable_code_interpreter', 'N/A')}\n\n")
            
            # Directory Structure
            f.write("## Session Structure\n\n")
            f.write("```\n")
            f.write(f"{os.path.basename(session_dir)}/\n")
            f.write("├── README.md (this file)\n")
            f.write("├── problem.md (original problem)\n")
            f.write("├── final_answer.md (Professor's final answer)\n")
            f.write("├── professor_iterations/ (Professor-level self-evolve iterations)\n")
            f.write("│   ├── iteration_1/\n")
            f.write("│   │   ├── README.md (iteration overview)\n")
            f.write("│   │   ├── qa1_prompt_response/ (Triple-QA Step 1)\n")
            f.write("│   │   │   ├── README.md\n")
            f.write("│   │   │   ├── professor_generation.md\n")
            f.write("│   │   │   └── workers/ (Workers for this QA step)\n")
            f.write("│   │   │       ├── worker_1_specialist/\n")
            f.write("│   │   │       └── worker_2_specialist/\n")
            f.write("│   │   ├── qa2_response_evaluation/ (Triple-QA Step 2)\n")
            f.write("│   │   │   ├── README.md\n")
            f.write("│   │   │   ├── evaluation.md\n")
            f.write("│   │   │   └── evaluator_reasoning.md\n")
            f.write("│   │   └── qa3_synthesis_refinement/ (Triple-QA Step 3)\n")
            f.write("│   │       ├── README.md\n")
            f.write("│   │       ├── refinement_analysis.md\n")
            f.write("│   │       └── refined_prompt.md\n")
            f.write("│   ├── iteration_2/\n")
            f.write("│   └── iteration_3/\n")
            f.write("└── summary.json (raw data)\n")
            f.write("```\n\n")
            
            # Overview sections
            prof_evolve = results.get('professor_evolve_info')
            consultation_summary = results.get('consultation_summary', {})
            
            f.write("## Overview\n\n")
            f.write("### Professor-Level Evolution\n")
            f.write(f"- Total iterations: {prof_evolve.get('total_iterations', 0) if prof_evolve else 0}\n")
            f.write("- Each iteration contains its own Worker consultations\n")
            f.write("- See [professor_iterations/](professor_iterations/) for details\n\n")
            
            f.write("### Worker Consultations\n")
            f.write(f"- Total consultations: {consultation_summary.get('total_consultations', 0)}\n")
            f.write(f"- Workers created: {consultation_summary.get('workers_created', 0)}\n")
            f.write("- Workers are organized by Professor iteration\n")
            f.write("- Each Worker includes complete self-evolve traces\n\n")
            
        # 2. Save problem.md
        problem_path = os.path.join(session_dir, "problem.md")
        with open(problem_path, 'w', encoding='utf-8') as f:
            f.write("# Original Problem\n\n")
            f.write("```\n")
            f.write(str(results.get('question', 'N/A')))
            f.write("\n```\n")
        
        # 3. Save final_answer.md
        final_answer_path = os.path.join(session_dir, "final_answer.md")
        with open(final_answer_path, 'w', encoding='utf-8') as f:
            f.write("# Professor's Final Answer\n\n")
            f.write("```\n")
            f.write(str(results.get('final_answer', 'N/A')))
            f.write("\n```\n")
        
        # 4. Save Professor evolution iterations with Triple-QA folder structure
        prof_evolve = results.get('professor_evolve_info')
        detailed_consultations = results.get('detailed_consultations', [])
        
        if prof_evolve:
            # Group workers by Professor iteration (assuming workers are called sequentially per iteration)
            consultation_summary = results.get('consultation_summary', {})
            
            # Create mapping of workers to Professor iterations
            total_iterations = prof_evolve.get('total_iterations', 0)
            workers_per_iter = len(detailed_consultations) // max(total_iterations, 1) if total_iterations > 0 else 0
            
            for it in prof_evolve.get('iterations', []):
                iter_num = it.get('iteration')
                iter_dir = os.path.join(session_dir, "professor_iterations", f"iteration_{iter_num}")
                
                # Create Triple-QA directories
                qa1_dir = os.path.join(iter_dir, "qa1_prompt_response")
                qa2_dir = os.path.join(iter_dir, "qa2_response_evaluation") 
                qa3_dir = os.path.join(iter_dir, "qa3_synthesis_refinement")
                workers_dir = os.path.join(qa1_dir, "workers")
                
                os.makedirs(iter_dir, exist_ok=True)
                os.makedirs(qa1_dir, exist_ok=True)
                os.makedirs(qa2_dir, exist_ok=True)
                os.makedirs(qa3_dir, exist_ok=True)
                os.makedirs(workers_dir, exist_ok=True)
                
                # Create iteration README
                iter_readme_path = os.path.join(iter_dir, "README.md")
                with open(iter_readme_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Professor Iteration {iter_num}\n\n")
                    f.write("## SE-Agents Triple-QA Architecture\n\n")
                    f.write("This iteration demonstrates the **Self-Evolve mechanism's Triple-QA structure**:\n\n")
                    f.write("### QA1: Prompt → Response\n")
                    f.write("- **Goal**: Generate initial response to the refined prompt\n")
                    f.write("- **Process**: Professor coordinates with specialist Workers\n")
                    f.write("- **Output**: Comprehensive answer incorporating Worker expertise\n")
                    f.write("- **Location**: [qa1_prompt_response/](qa1_prompt_response/)\n\n")
                    
                    f.write("### QA2: Response → Evaluation\n")
                    f.write("- **Goal**: Independent assessment of response quality\n")
                    f.write("- **Process**: Evaluator analyzes the generated response\n")
                    f.write("- **Output**: Detailed feedback and quality assessment\n")
                    f.write("- **Location**: [qa2_response_evaluation/](qa2_response_evaluation/)\n\n")
                    
                    f.write("### QA3: Synthesis → Refinement\n")
                    f.write("- **Goal**: Create improved prompt with deterministic hints\n")
                    f.write("- **Process**: Refiner synthesizes insights from QA1 + QA2\n")
                    f.write("- **Output**: Enhanced prompt for next iteration\n")
                    f.write("- **Location**: [qa3_synthesis_refinement/](qa3_synthesis_refinement/)\n\n")
                    
                    # Estimate which workers belong to this iteration
                    start_worker_idx = (iter_num - 1) * workers_per_iter
                    end_worker_idx = min(iter_num * workers_per_iter, len(detailed_consultations))
                    
                    if start_worker_idx < len(detailed_consultations):
                        f.write("## Workers Consulted in QA1\n\n")
                        for w_idx in range(start_worker_idx, end_worker_idx):
                            if w_idx < len(detailed_consultations):
                                consultation = detailed_consultations[w_idx]
                                worker_name = consultation.get('specialization', 'Unknown').replace(' ', '_')
                                f.write(f"- [Worker {w_idx+1}: {consultation.get('specialization', 'Unknown')}](qa1_prompt_response/workers/worker_{w_idx+1}_{worker_name}/)\n")
                
                # === QA1: Prompt → Response ===
                qa1_readme_path = os.path.join(qa1_dir, "README.md")
                with open(qa1_readme_path, 'w', encoding='utf-8') as f:
                    f.write(f"# QA1: Prompt → Response (Iteration {iter_num})\n\n")
                    f.write("## Triple-QA Step 1: Generate Response\n\n")
                    f.write("This step represents the **Prompt → Response** phase of the Self-Evolve mechanism:\n")
                    f.write("- Professor receives refined prompt (with deterministic hints from previous iterations)\n")
                    f.write("- Professor dynamically spawns specialized Workers based on problem complexity\n")
                    f.write("- Each Worker applies self-evolve to assigned sub-tasks\n")
                    f.write("- Professor synthesizes Worker outputs into comprehensive response\n\n")
                    
                    f.write("## Files in This QA Step\n\n")
                    f.write("- [professor_generation.md](professor_generation.md) - Professor's generation process and final response\n")
                    f.write("- [workers/](workers/) - All Worker consultations for this step\n\n")
                
                # QA1: Professor Generation
                prof_gen_path = os.path.join(qa1_dir, "professor_generation.md")
                with open(prof_gen_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Professor Generation - Iteration {iter_num}\n\n")
                    
                    # Input Prompt
                    refined_q = it.get('refined_question')
                    if refined_q and iter_num > 1:
                        f.write("## Input: Refined Prompt (with Deterministic Hints)\n\n")
                        f.write("```\n")
                        f.write(str(refined_q))
                        f.write("\n```\n\n")
                        f.write("*This prompt includes accumulated insights from previous iterations*\n\n")
                    else:
                        f.write("## Input: Original Problem\n\n")
                        f.write("```\n")
                        f.write(str(it.get('question', 'N/A')))
                        f.write("\n```\n\n")
                    
                    # Professor Reasoning Process
                    if it.get('reasoning_summary'):
                        f.write("## Professor Reasoning Process\n\n")
                        f.write("```\n")
                        f.write(str(it.get('reasoning_summary')))
                        f.write("\n```\n\n")
                    
                    # Generated Response
                    f.write("## Output: Generated Response\n\n")
                    f.write("```\n")
                    f.write(str(it.get('answer', 'N/A')))
                    f.write("\n```\n\n")
                    
                    f.write("---\n")
                    f.write(f"*QA1 completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
                
                # === QA2: Response → Evaluation ===
                qa2_readme_path = os.path.join(qa2_dir, "README.md")
                with open(qa2_readme_path, 'w', encoding='utf-8') as f:
                    f.write(f"# QA2: Response → Evaluation (Iteration {iter_num})\n\n")
                    f.write("## Triple-QA Step 2: Evaluate Response\n\n")
                    f.write("This step represents the **Response → Evaluation** phase of the Self-Evolve mechanism:\n")
                    f.write("- Evaluator independently assesses the response from QA1\n")
                    f.write("- Provides detailed feedback on mathematical accuracy, reasoning quality, completeness\n")
                    f.write("- Identifies strengths to preserve and weaknesses to address\n")
                    f.write("- Acts as quality gate for the self-evolve process\n\n")
                    
                    f.write("## Files in This QA Step\n\n")
                    f.write("- [evaluation.md](evaluation.md) - Evaluator's assessment and feedback\n")
                    f.write("- [evaluator_reasoning.md](evaluator_reasoning.md) - Evaluator's detailed reasoning process\n\n")
                
                # QA2: Evaluation
                eval_path = os.path.join(qa2_dir, "evaluation.md")
                with open(eval_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Evaluation Feedback - Iteration {iter_num}\n\n")
                    f.write("## Input: Response from QA1\n\n")
                    f.write("```\n")
                    f.write(str(it.get('answer', 'N/A')))
                    f.write("\n```\n\n")
                    
                    f.write("## Output: Evaluation Feedback\n\n")
                    f.write("```\n")
                    f.write(str(it.get('evaluation_feedback', 'N/A')))
                    f.write("\n```\n\n")
                    
                    f.write("---\n")
                    f.write(f"*QA2 completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
                
                # QA2: Evaluator Reasoning (if available)
                if it.get('evaluator_reasoning_summary'):
                    eval_reasoning_path = os.path.join(qa2_dir, "evaluator_reasoning.md")
                    with open(eval_reasoning_path, 'w', encoding='utf-8') as f:
                        f.write(f"# Evaluator Reasoning Process - Iteration {iter_num}\n\n")
                        f.write("## Detailed Reasoning\n\n")
                        f.write("```\n")
                        f.write(str(it.get('evaluator_reasoning_summary')))
                        f.write("\n```\n\n")
                
                # === QA3: Synthesis → Refinement ===
                qa3_readme_path = os.path.join(qa3_dir, "README.md")
                with open(qa3_readme_path, 'w', encoding='utf-8') as f:
                    f.write(f"# QA3: Synthesis → Refinement (Iteration {iter_num})\n\n")
                    f.write("## Triple-QA Step 3: Synthesize and Refine\n\n")
                    f.write("This step represents the **Synthesis → Refinement** phase of the Self-Evolve mechanism:\n")
                    f.write("- Refiner analyzes insights from QA1 (response) and QA2 (evaluation)\n")
                    f.write("- Synthesizes successful approaches and identified weaknesses\n")
                    f.write("- Creates **deterministic hints** for the next iteration\n")
                    f.write("- Produces refined prompt that builds on accumulated knowledge\n\n")
                    
                    f.write("## Files in This QA Step\n\n")
                    f.write("- [refinement_analysis.md](refinement_analysis.md) - Refiner's analysis and reasoning\n")
                    if iter_num < total_iterations:
                        f.write("- [refined_prompt.md](refined_prompt.md) - Enhanced prompt for next iteration\n\n")
                    else:
                        f.write("- *No refined prompt (final iteration)*\n\n")
                
                # QA3: Refinement Analysis (if available)
                if it.get('refiner_reasoning_summary'):
                    refine_analysis_path = os.path.join(qa3_dir, "refinement_analysis.md")
                    with open(refine_analysis_path, 'w', encoding='utf-8') as f:
                        f.write(f"# Refinement Analysis - Iteration {iter_num}\n\n")
                        f.write("## Refiner Reasoning Process\n\n")
                        f.write("```\n")
                        f.write(str(it.get('refiner_reasoning_summary')))
                        f.write("\n```\n\n")
                        
                        f.write("---\n")
                        f.write(f"*QA3 completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
                
                # QA3: Refined Prompt (for next iteration, if not final)
                if iter_num < total_iterations:
                    # We'll need to get the refined prompt from the next iteration
                    next_iteration = None
                    for next_it in prof_evolve.get('iterations', []):
                        if next_it.get('iteration') == iter_num + 1:
                            next_iteration = next_it
                            break
                    
                    if next_iteration and next_iteration.get('refined_question'):
                        refined_prompt_path = os.path.join(qa3_dir, "refined_prompt.md")
                        with open(refined_prompt_path, 'w', encoding='utf-8') as f:
                            f.write(f"# Refined Prompt for Iteration {iter_num + 1}\n\n")
                            f.write("## Output: Enhanced Prompt with Deterministic Hints\n\n")
                            f.write("```\n")
                            f.write(str(next_iteration.get('refined_question')))
                            f.write("\n```\n\n")
                            f.write("*This prompt will be used as input for the next iteration's QA1 step*\n\n")
                
                # Save workers for this iteration under QA1
                for w_idx in range(start_worker_idx, end_worker_idx):
                    if w_idx < len(detailed_consultations):
                        consultation = detailed_consultations[w_idx]
                        worker_name = consultation.get('specialization', 'Unknown').replace(' ', '_')
                        worker_dir = os.path.join(workers_dir, f"worker_{w_idx+1}_{worker_name}")
                        os.makedirs(worker_dir, exist_ok=True)
                        
                        # Save worker overview
                        worker_readme_path = os.path.join(worker_dir, "README.md")
                        with open(worker_readme_path, 'w', encoding='utf-8') as f:
                            f.write(f"# Worker {w_idx+1}: {consultation.get('specialization', 'Unknown')}\n\n")
                            f.write(f"**Worker ID**: {consultation.get('worker_id', 'N/A')}\n")
                            f.write(f"**Professor Iteration**: {iter_num}\n")
                            f.write("**Triple-QA Phase**: QA1 (Prompt → Response)\n\n")
                            
                            f.write("## Task Assignment\n\n")
                            f.write("```\n")
                            f.write(str(consultation.get('task', 'N/A')))
                            f.write("\n```\n\n")
                            
                            if consultation.get('enhanced_task'):
                                f.write("## Professor's Enhanced Instructions\n\n")
                                f.write("```\n")
                                f.write(str(consultation.get('enhanced_task')))
                                f.write("\n```\n\n")
                            
                            session_details = consultation.get('session_details', {})
                            iterations = session_details.get('iterations', [])
                            
                            f.write("## Worker Self-Evolve Summary\n\n")
                            f.write(f"- Total self-evolve iterations: {len(iterations)}\n")
                            f.write("- Final answer: See [final.md](final.md)\n\n")
                            
                            f.write("## Self-Evolve Iterations\n\n")
                            for iter_num_w, _ in enumerate(iterations, 1):
                                f.write(f"- [Iteration {iter_num_w}](iteration_{iter_num_w}.md)\n")
                        
                        # Save each worker iteration with actual reasoning summaries
                        for iter_num_w, iteration in enumerate(iterations, 1):
                            worker_iter_path = os.path.join(worker_dir, f"iteration_{iter_num_w}.md")
                            with open(worker_iter_path, 'w', encoding='utf-8') as f:
                                f.write(f"# Worker {w_idx+1} - Self-Evolve Iteration {iter_num_w}\n\n")
                                
                                # Handle refined question
                                refined_q_w = iteration.get('refined_question')
                                if refined_q_w and iter_num_w > 1:
                                    f.write("## Refined Task (with Deterministic Hints)\n\n")
                                    f.write("```\n")
                                    f.write(str(refined_q_w))
                                    f.write("\n```\n\n")
                                else:
                                    f.write("## Original Task\n\n")
                                    f.write("```\n")
                                    f.write(str(iteration.get('question', 'N/A')))
                                    f.write("\n```\n\n")
                                
                                # Reasoning Summary from actual iteration data
                                reasoning_summary = iteration.get('reasoning_summary', '')
                                if reasoning_summary:
                                    f.write("## Worker Reasoning Process\n\n")
                                    f.write("```\n")
                                    f.write(str(reasoning_summary))
                                    f.write("\n```\n\n")
                                
                                # Answer
                                f.write("## Generated Answer\n\n")
                                f.write("```\n")
                                f.write(str(iteration.get('answer', 'N/A')))
                                f.write("\n```\n\n")
                                
                                # Evaluation
                                f.write("## Evaluation Feedback\n\n")
                                f.write("```\n")
                                f.write(str(iteration.get('evaluation_feedback', 'N/A')))
                                f.write("\n```\n\n")
                                
                                # Evaluator reasoning summary
                                evaluator_reasoning = iteration.get('evaluator_reasoning_summary', '')
                                if evaluator_reasoning:
                                    f.write("## Evaluator Reasoning\n\n")
                                    f.write("```\n")
                                    f.write(str(evaluator_reasoning))
                                    f.write("\n```\n\n")
                                
                                # Refiner reasoning summary
                                refiner_reasoning = iteration.get('refiner_reasoning_summary', '')
                                if refiner_reasoning:
                                    f.write("## Prompt Refiner Reasoning\n\n")
                                    f.write("```\n")
                                    f.write(str(refiner_reasoning))
                                    f.write("\n```\n\n")
                        
                        # Save worker final answer
                        worker_final_path = os.path.join(worker_dir, "final.md")
                        with open(worker_final_path, 'w', encoding='utf-8') as f:
                            f.write(f"# Worker {w_idx+1} - Final Answer\n\n")
                            f.write("```\n")
                            f.write(str(consultation.get('final_answer', 'N/A')))
                            f.write("\n```\n")
        
        # Save summary.json
        summary_path = os.path.join(session_dir, "summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"체계적인 세션 리포트가 저장되었습니다: {session_dir}")
        return index_path
        
    except Exception as e:
        print(f"[ERROR] Markdown 저장 실패: {e}")
        import traceback
        print(f"상세 에러: {traceback.format_exc()}")
        return None


def professor_graduate_example():
    """Example demonstrating Professor + Graduate Self-Evolve system with Responses API"""
    
    os.makedirs("./self_evolve/logs", exist_ok=True)
    setup_logging(log_level="INFO", log_file="./self_evolve/logs/professor_graduate_responses.jsonl", json_logs=True)
    
    # Configure the system for Responses API
    config = FrameworkConfig(
        generator_config=ModelConfig(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name=os.getenv("PROFESSOR_MODEL", "o4-mini"),  # Professor uses gpt-4.1-mini by default
            reasoning_effort="high",
            truncation="auto",
            temperature=0.7
        ),
        evaluator_config=ModelConfig(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name=os.getenv("EVALUATOR_MODEL", "o4-mini"),  # Evaluator for graduates
            enable_code_interpreter=True,
            reasoning_effort="high",
            truncation="auto",
            temperature=0.3
        ),
        # 분리된 Prompt Refiner 모델 설정 (Evaluator와 다르게 구성 가능)
        refiner_config=ModelConfig(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name=os.getenv("REFINER_MODEL", "o4-mini"),  # 별도로 지정, 기본은 evaluator와 동일
            temperature=0.5,
            reasoning_effort="high",
            truncation="auto"
        ),
        worker_config=WorkerConfig(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name=os.getenv("WORKER_MODEL", "o4-mini"),
            enable_code_interpreter=True,
            reasoning_effort="high",
            max_self_evolve_iterations=int(os.getenv("WORKER_MAX_SELF_EVOKE_ITERS", "4")),
        )
    )
    
    # Optional: Force non-streaming for testing (set FORCE_NON_STREAMING=1 environment variable)
    # if os.getenv("FORCE_NON_STREAMING") == "1":
    #     print("🔧 TESTING MODE: Forcing non-streaming for all API calls")
    #     config.generator_config.stream = False
    #     config.evaluator_config.stream = False
    #     config.refiner_config.stream = False
    #     config.worker_config.stream = False
    
    # Initialize Professor Model with enhanced Responses API support
    professor = ProfessorModel(config)
    
    # Load problem from XML file
    try:
        problem_file = os.getenv("PROBLEM_FILE", "./self_evolve/examples/problems/IC-RL.xml")
        with open(problem_file, "r", encoding="utf-8") as f:
            question = f.read()
            question = question + "\n\nsolve this problem with consulting the graduate_specialist and perfect mathematical rigor."
    except FileNotFoundError:
        print("Warning: Problem file not found. Using default ord density problem.")
        question = """
<problem id="ord_density" points="4">
    <statement>
        For a positive integer <var>n</var>, let
        <math><![CDATA[v_p(n)]]></math> denote the largest integer
        <math><![CDATA[v]]></math> such that
        <math><![CDATA[p^{\,v}\mid n]]></math>.
        For a prime <var>p</var> and an integer <var>a</var> with
        <math><![CDATA[a \not\equiv 0 \pmod{p}]]></math>, let
        <math><![CDATA[\operatorname{ord}_p(a)]]></math> denote the smallest positive integer
        <math><![CDATA[o]]></math> such that
        <math><![CDATA[a^{\,o}\equiv 1 \pmod{p}]]></math>.
        <br/><br/>
        For <math><![CDATA[x>0]]></math>, define
        <math><![CDATA[
            \operatorname{ord}_{p,x}(a)\;=\;
            \prod_{\substack{q\le x\\ q\text{ prime}}} q^{\,v_q\bigl(\operatorname{ord}_p(a)\bigr)}
            \;\;\prod_{\substack{q> x\\ q\text{ prime}}} q^{\,v_q(p-1)}\,.
        ]]></math>
        <br/><br/>
        Let <math><![CDATA[S_x]]></math> be the set of primes <var>p</var> satisfying
        <math><![CDATA[
            \operatorname{ord}_{p,x}(2)\;>\;\operatorname{ord}_{p,x}(3).
        ]]></math>
        <br/><br/>
        Denote by <math><![CDATA[d_x]]></math> the natural density of <math><![CDATA[S_x]]></math> in the primes,
        <math><![CDATA[
            d_x \;=\;
            \lim_{t\to\infty}\;
            \frac{\bigl|\{\,p\le t : p\in S_x\}\bigr|}
                 {\bigl|\{\,p\le t : p\text{ prime}\}\bigr|}.
        ]]></math>
        Define
        <math><![CDATA[
            d_\infty \;=\; \lim_{x\to\infty} d_x.
        ]]></math>
    </statement>

    <target>
        <expression><![CDATA[
            \bigl\lfloor 10^{6}\,d_\infty \bigr\rfloor
        ]]></expression>
    </target>
</problem>
"""
    
    print("=== Professor with Graduate Self-Evolve Specialists (Responses API) ===")
    print(f"Question: {question[:500]}...")
    print("-" * 80)
    
    # Professor-level Self-Evolve 루프 실행
    start_time = datetime.now()
    professor_iters = int(os.getenv("PROFESSOR_MAX_ITERS", "6"))
    session = professor.self_evolve(question, max_iterations=professor_iters)
    end_time = datetime.now()
    final_answer = session.final_answer
    
    print(f"\n{'='*80}")
    print("FINAL ANSWER FROM PROFESSOR:")
    print(f"{'='*80}")
    print(final_answer)
    
    # Display execution summary
    print(f"\nExecution Time: {(end_time - start_time).total_seconds():.2f} seconds")
    
    # Get and display consultation summary
    consultation_summary = professor.get_consultation_summary()
    print("\nGraduate Consultations Summary:")
    print(f"- Total consultations: {consultation_summary['total_consultations']}")
    print(f"- Graduate workers created: {consultation_summary['workers_created']}")
    print(f"- Response ID: {consultation_summary['current_response_id']}")
    
    if consultation_summary['consultations']:
        print("\nDetailed Consultations:")
        for i, consultation in enumerate(consultation_summary['consultations'], 1):
            print(f"\n  Consultation {i}:")
            print(f"  - Worker: {consultation['worker_id']}")
            print(f"  - Specialization: {consultation['specialization']}")
            print(f"  - Self-evolve iterations: {consultation['iterations']}")
            print(f"  - Final answer: {consultation['final_answer']}")
            print(f"  - Task: {consultation['task']}")
    
    # Demonstrate conversation continuation
    if consultation_summary['current_response_id']:
        print(f"\n{'-'*50}")
        print("Testing conversation continuation...")
        follow_up = "Can you summarize the key insights from the specialists' work?"
        try:
            continuation_response = professor.continue_conversation(follow_up)
            print(f"Follow-up question: {follow_up}")
            print(f"Professor's response: {continuation_response[:300]}...")
        except Exception as e:
            print(f"Conversation continuation failed: {e}")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create session directory
    import uuid
    session_id = str(uuid.uuid4())[:8]
    session_dir = f"./self_evolve/examples/results/logs/{session_id}"
    os.makedirs(session_dir, exist_ok=True)
    
    output_path = os.path.join(session_dir, f"professor_graduate_responses_{timestamp}.json")
    
    try:
        # 교수 단계 자기 발전 세션도 저장
        professor_evolve_info = {
            "total_iterations": session.total_iterations,
            "iterations": [
                {
                    "iteration": it.iteration,
                    "refined_question": it.refined_question or it.question,
                    "answer": it.answer,
                    "reasoning_summary": it.reasoning_summary,
                    "evaluation_feedback": it.evaluation_feedback,
                    "evaluator_reasoning_summary": it.evaluator_reasoning_summary,
                    "refiner_reasoning_summary": it.refiner_reasoning_summary,
                } for it in session.iterations
            ]
        }
        
        results = {
            "timestamp": timestamp,
            "api_version": "responses_api",
            "question": question,
            "final_answer": final_answer,
            "execution_time_seconds": (end_time - start_time).total_seconds(),
            "consultation_summary": consultation_summary,
            "detailed_consultations": professor.consultation_history,
            "system_config": {
                "professor_model": config.generator_config.model_name,
                "worker_model": config.worker_config.model_name,
                "evaluator_model": config.evaluator_config.model_name,
                "refiner_model": config.refiner_config.model_name,
                "worker_max_self_evolve_iterations": config.worker_config.max_self_evolve_iterations,
                "reasoning_effort": config.generator_config.reasoning_effort,
                "enable_code_interpreter": config.generator_config.enable_code_interpreter
            },
            "professor_evolve_info": professor_evolve_info
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\nDetailed results saved to {output_path}")
        
        # Save markdown report
        markdown_path = save_session_to_markdown(results, output_path, session_dir)
        if markdown_path:
            print(f"Markdown 보고서 저장됨: {markdown_path}")
            print(f"세션 디렉토리: {session_dir}")
            
    except Exception as e:
        print(f"[Warning] Failed to save results: {e}")
        



if __name__ == "__main__":
    print("Running full Professor + Graduate example with Responses API...")
    professor_graduate_example() 